# Understanding Brief: reconvergence generated tests

## One-Sentence Test Purpose

This test checks whether subgroup and workgroup control-flow execution, and maximal reconvergence, produce the ballot and stored-value behavior required by the selected Vulkan shader execution mode.

## Background Knowledge

### Reconvergence and subgroup operations

A subgroup is the set of shader invocations that participate in subgroup operations together. Divergent control flow can leave different invocations at different program points. Reconvergence rules determine which invocations participate when later control flow or subgroup operations execute. `subgroupElect()` selects one active invocation, while `subgroupBallot(true)` records the active invocation mask.

Why it matters here:
- The generated program deliberately mixes divergent conditions, loops, switches, function calls, returns, and ballots.
- The test compares the device's observed masks with a CPU simulation that tracks active invocations at each generated operation.

### Uniform-control-flow and maximal-reconvergence execution modes

The Vulkan feature `shaderSubgroupUniformControlFlow` supports the `SubgroupUniformControlFlowKHR` execution mode. The `shaderMaximalReconvergence` feature supports `MaximallyReconvergesKHR`. The source emits `[[subgroup_uniform_control_flow]]` for the SUCF families and `[[maximally_reconverges]]` for `maximal`; the latter also enables `GL_EXT_maximal_reconvergence`.

Why it matters here:
- SUCF results are judged for the fully converged observations that the mode requires.
- Maximal cases compare all recorded ballot values exactly with the CPU reference.
- The Vulkan feature descriptions define these modes as implementation support for the corresponding SPIR-V execution modes, while the shader specification describes the execution consequences for maximal reconvergence and helper invocations.

## One Concrete Example

Consider a compute case under `dEQP-VK.reconvergence.subgroup_uniform_control_flow_elect.compute.nesting2.0.0`.

The host chooses `sizeX = 7`, `sizeY = 13`, `nesting2`, seed `0`, and test index `0`. The generator emits a short random sequence such as a divergent `if`, a store, and an elect-controlled region. The exact sequence is generated from the case seed and is not fixed by this brief.

Conceptually, one generated fragment has this shape:

```glsl
/// Conceptual shape only. The actual source is generated from the case seed.
if (testBit(uvec4(mask0, mask1, mask2, mask3), gl_SubgroupInvocationID)) {
    outputC.loc[gl_LocalInvocationIndex]++;
    outputB.b[(outLoc++) * invocationStride + gl_LocalInvocationIndex].x = literal;
}
outputC.loc[gl_LocalInvocationIndex]++;
outputB.b[(outLoc++) * invocationStride + gl_LocalInvocationIndex] = subgroupBallot(true).xy;
if (subgroupElect()) {
    // generated work may include a break, return, or nested operation here
}
```

For the elect families, the generated `elect()` helper stores `int(subgroupElect()) + 1`, so the elected lane records `2` and other participating lanes record `1`. Ballot families store the subgroup ballot mask. The source emits the actual generated body after the common declarations and prologue.

## End-to-End Test Flow

```text
[host] select the test family, shader stage, nesting level, seed, and generated test index
[host] create the random program and simulate it when SUCF validation needs a program with a nonuniform result
[host] generate GLSL with subgroup declarations, storage-buffer bindings, push constants, and the selected execution-mode attribute
[host] create the pipeline, pass `sizeX` and `sizeY` as specialization constants, and initialize input and output buffers
[host] run the counting pass, clear output buffers, then run the generated shader
[device] execute one compute dispatch or the selected graphics pipeline and record literals, ballots, and location counters
[host] wait for completion, invalidate the result allocation, and run the same generated program through the CPU simulator
[host] compare the GPU output with the reference using the selected test family's matching rule
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- The random program is built from operations such as divergent masks, uniform and varying loops, infinite loops with elect-controlled exits, switches, calls, returns, ballots, stores, and noise. The generator retries SUCF programs until the CPU simulation finds a nonuniform ballot result.
- `initPrograms` emits GLSL version 450, subgroup ballot/vote/partitioned-operation extensions, and `GL_EXT_subgroup_uniform_control_flow`; maximal cases additionally require `GL_EXT_maximal_reconvergence`.
- The compute shader uses specialization constants for `local_size_x_id = 0` and `local_size_y_id = 1`. The source selects SPIR-V 1.3 in `vk::ShaderBuildOptions`.
- The generated entry point receives `[[subgroup_uniform_control_flow]]` for SUCF cases or `[[maximally_reconverges]]` for maximal cases before `main`.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| `InputA` storage buffer, binding 0 | yes | yes | read | no | Supplies deterministic values used by generated conditions and loops. |
| `OutputB` coherent storage buffer, binding 1 | yes | yes | written | yes | Stores literals, elected values, and ballot observations. |
| `OutputC` coherent storage buffer, binding 2 | yes | yes | written | yes | Records output-location counts used to size and interpret observations. |
| Push-constant `PC` | yes | yes | read | no | Carries `invocationStride`, dimensions, and indexing controls. |
| `OutputP` storage buffer, binding 3 in graphics paths | yes | yes | written | yes | Tracks subgroup IDs, subgroup size, invocation counts, and graphics indexing facts. |
| CPU `RandomProgram` reference | no | no | no | yes | Mirrors the generated control flow and supplies the expected output. |

`shared` variables are not used as a substitute for these host-created resources in the generated compute interface. The compute shader's `OutputC`, `OutputB`, and `InputA` declarations are coherent storage buffers.

## What Is Checked

- The host reads the device-written `OutputB` and `OutputC` data after a compute-to-host pipeline barrier and queue wait.
- The CPU executes the same random operation sequence with the selected subgroup size and builds a reference vector.
- Maximal reconvergence requires exact equality between every recorded GPU ballot/value and the reference; mismatches fail the case and are logged.
- SUCF cases search the GPU result for each expected fully converged reference mask. Elect cases require the elected lane/value pattern, while ballot cases require the full subgroup mask. A missing matching output fails the case.
- Graphics paths use the same reference principle and add stage-specific bookkeeping for fragments, vertices, tessellation invocations, or geometry primitives.

## Behavior Parameter Identification

> **Behavior parameter:** test family
>
> **Candidate values:** `subgroup_uniform_control_flow_elect`, `subgroup_uniform_control_flow_ballot`, `workgroup_uniform_control_flow_elect`, `workgroup_uniform_control_flow_ballot`, `maximal`

The five test-family values change the execution-mode or subgroup-operation contract being tested. Shader stage, nesting, seed, and test index select the generated workload and are secondary dimensions.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `subgroup_uniform_control_flow_elect` | Incorrect subgroup-uniform reconvergence or `subgroupElect()` result in generated divergent control flow. |
| `subgroup_uniform_control_flow_ballot` | Incorrect subgroup-uniform reconvergence or subgroup ballot mask in generated divergent control flow. |
| `workgroup_uniform_control_flow_elect` | Incorrect workgroup-uniform control-flow behavior or `subgroupElect()` result. |
| `workgroup_uniform_control_flow_ballot` | Incorrect workgroup-uniform control-flow behavior or subgroup ballot mask. |
| `maximal` | Incorrect maximal-reconvergence execution or ballot/value result compared with the CPU reference. |

## Important Variations and Special Cases

- The five generated families always include compute paths. The current `stTypes` list includes fragment paths, but the source skips non-compute stages unless the family is `maximal`; the graphics-stage entries are therefore registered only for `maximal` in the current configuration.
- Non-maximal families keep `nesting2` through `nesting4`. Maximal compute keeps `nesting2` through `nesting6`. Maximal fragment cases use `nNdx = 7`, add Amber fragment cases, and do not enter the nesting loop.
- Each nesting group has eight seed groups. The generated count is 250 cases for nesting 2 to 4, 100 for nesting 5, and 50 for nesting 6 before the main/experimental split.
- `createTests` sends indices below `numTests / 5` to the main tree and the remaining indices to the experimental tree. Both packages register the root name `reconvergence`, through `createTests` and `createTestsExperimental` respectively.
- Compute cases use `sizeX = 7`, `sizeY = 13`; fragment cases use a 32 by 32 framebuffer. If full subgroups are supported, the runtime adjusts compute specialization dimensions to subgroup-aligned values.
- Maximal fragment generation also includes the Amber cases `terminate_invocation`, `demote_invocation`, `demote_entire_quad`, `demote_half_quad_top`, `demote_half_quad_right`, `demote_half_quad_bottom`, `demote_half_quad_left`, `demote_half_quad_slash`, and `demote_half_quad_backslash` under `maximal/<group name>`.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Test-family and stage registration | [createTests](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L7786-L7825) | Defines the five direct generated families, their stage filter, and their relationship to the root. |
| Nesting, seeds, counts, dimensions, and split | [matrix construction](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L7837-L7938) | Defines exact generated parameter values and main/experimental routing. |
| Root declarations | [reconvergence header](../../../modules/vulkan/reconvergence/vktReconvergenceTests.hpp#L30-L36) | Declares main and experimental creation functions. |
| Main and experimental package registration | [test package](../../../modules/vulkan/vktTestPackage.cpp#L1387-L1407) | Shows both packages register the same root name with different constructors. |
| Feature and support checks | [checkSupport](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L4395-L4433) | Defines Vulkan version, subgroup operation, stage, UCF, maximal, and compute-limit gates. |
| Shader generation | [initPrograms](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L4547-L5006) | Defines extensions, resources, execution-mode attributes, and SPIR-V target. |
| Operation generation | [random generator](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L1010-L1633) | Builds and simulates the generated operation sequence. |
| Shader code printer | [printCode](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L1752-L2012) | Maps operation records to GLSL control flow and observation writes. |
| Compute result checking | [compute iterate](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L5220-L5314) | Runs the shader, executes the CPU reference, and compares outputs. |
| Compute failure rules | [calculateAndLogResult](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L5317-L5420) | Defines exact maximal and SUCF comparison behavior. |
| Feature semantics | [uniform-control-flow features](../../../vulkan-docs/src/chapters/features.adoc#L5147-L5170) and [maximal-reconvergence features](../../../vulkan-docs/src/chapters/features.adoc#L8602-L8624) | Defines the Vulkan feature fields and corresponding SPIR-V execution modes. |
| Maximal helper-invocation rule | [shader execution rule](../../../vulkan-docs/src/chapters/shaders.adoc#L3755-L3767) | Grounds the helper-invocation consequence of maximal reconvergence. |

## Questions / Risk Points for User Audit

- The exact random shader text depends on the selected seed and index. The conceptual example is intentionally not a claim about one literal generated case.
- The source contains disabled vertex, tessellation, and geometry registration behind `INCLUDE_GRAPHICS_TESTS`; this brief treats those paths as source evidence, not current registered coverage.
- The current page groups the delegated `terminate_invocation` branch under this implementation page, but its four direct leaves are documented by the separate delegated page.
- The Vulkan chapters describe the feature fields and maximal helper-invocation rule. Detailed SPIR-V reconvergence wording is outside the local chapter excerpts used here.

## Conversion Notes for Final Wiki Rewrite

- Keep the five generated families as the primary behavioral axis.
- Use one representative compute walkthrough with a conceptual generated body. Do not present the conceptual body as an exact fixed shader.
- Keep the exact root and direct-child names in one parseable registration tree, and mark `terminate_invocation` as registration only.
- Preserve the main and experimental package registrations and the 1/5 versus 4/5 split in parameter or pruning text.
- Distill the prerequisite explanation into short bullets and keep generated artifacts, resources, runtime comparison, and failure mapping in their dedicated sections.
- Copy the failure mapping table into the final page unchanged.
