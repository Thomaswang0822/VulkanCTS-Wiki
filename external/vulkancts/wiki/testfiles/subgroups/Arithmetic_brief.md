# Understanding Brief: `subgroups.arithmetic`

## One-Sentence Test Purpose

This test checks whether supported subgroup reduction, inclusive-scan, and exclusive-scan operations return the required cumulative value for active invocations across the registered operators, data types, shader stages, and subgroup-size modes.

## Background Knowledge

### Subgroup arithmetic scope and scan boundaries

A Vulkan subgroup is the scope instance used by these group operations. The Vulkan specification defines reduction as applying an operator to all participating values, an inclusive scan as applying it through the current invocation, and an exclusive scan as stopping before the current invocation. The order of application is implementation-dependent.

Why it matters here:
- The expected input range changes with the scan form, so each invocation can have a different result.
- Floating-point addition and multiplication are compared with a tolerance because a legal implementation order can change rounding.

### Active invocations and identities

The identity value leaves an operation unchanged, such as `0` for addition, `1` for multiplication, all one bits for AND, and `0` for OR or XOR. A ballot records which invocations are active at the point where it executes. Folding only ballot-selected values from the identity gives a shader-computed reference for the same active set used by the subgroup operation.

Why it matters here:
- The shader performs one check in ordinary control flow and a second check in a branch taken only by odd subgroup invocation IDs.
- An exclusive scan can have an empty prefix. The reference must then remain the identity.

## One Concrete Example

For `dEQP-VK.subgroups.arithmetic.compute.subgroupinclusiveadd_uint`, invocation `i` starts from `uint(0)` and adds active `data[0]` through `data[i]`. It compares that reference with `subgroupInclusiveAdd(data[i])`. Every odd invocation repeats the comparison while only odd invocations are active in that branch. Bit 0 records the first comparison and bit 1 records the divergent comparison, so the final value must be `0x3`.

This is reconstructed from [`getIndexVars()` and `getTestSrc()`](../../../modules/vulkan/subgroups/vktSubgroupsArithmeticTests.cpp#L179-L249), with the surrounding compute shader supplied by [`initStdPrograms()`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L1406-L1434).

## End-to-End Test Flow

```text
[host] select scan form, operator, vector type, shader-stage family, and optional required subgroup size
[host] reject unsupported subgroup features, stages, formats, storage types, or size-control modes
[host] generate stage-specific GLSL around the arithmetic test body and compile it for SPIR-V 1.3 or 1.4
[host] allocate and initialize nonzero input data plus the stage-specific result target
[host] dispatch, draw, or trace using the common subgroup harness
[device] compute a ballot-based reference and compare it with the selected subgroup arithmetic operation
[device] repeat the comparison in odd-invocation divergent control flow and write a two-bit result
[host] wait, read back the result buffer or framebuffer output, and require every checked value to equal 0x3
[host] for required-size compute or mesh cases, repeat across every supported power-of-two subgroup size
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- [`getExtHeader()`](../../../modules/vulkan/subgroups/vktSubgroupsArithmeticTests.cpp#L172-L177) enables subgroup arithmetic and ballot extensions plus extensions required by the selected data type.
- [`getTestSrc()`](../../../modules/vulkan/subgroups/vktSubgroupsArithmeticTests.cpp#L194-L249) emits the reference loops, subgroup built-in call, comparisons, and two-bit result.
- [`initPrograms()`](../../../modules/vulkan/subgroups/vktSubgroupsArithmeticTests.cpp#L262-L277) selects SPIR-V 1.3 for compute and ordinary graphics, and SPIR-V 1.4 for ray tracing and mesh shading. [`initFrameBufferPrograms()`](../../../modules/vulkan/subgroups/vktSubgroupsArithmeticTests.cpp#L252-L260) uses SPIR-V 1.3.
- Common builders wrap the test body in compute, graphics, mesh, ray-tracing, or framebuffer-stage GLSL.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Nonzero input data | yes | yes | read | no | Supplies one value per possible subgroup invocation for the reference and tested operation. |
| `result[]` storage buffer | yes | yes | written | yes | Compute, graphics, mesh, and ray-tracing paths store one two-bit validation result per executed element. |
| Framebuffer-path uniform buffer | yes | yes | read | no | Stages that cannot use the ordinary SSBO path receive the same input values through `std140` uniform storage. |
| `R32_UINT` color attachment and transfer buffer | yes | yes | written, then copied | yes | Framebuffer variants encode `tempRes` through stage outputs and recover the integer result for the common `0x3` check. |
| Required-subgroup-size pipeline state | yes | yes | controls execution | no | Compute and mesh variants request each supported power-of-two subgroup size. |

## What Is Checked

- Each invocation computes a reference over the active invocation IDs selected by its scan form.
- Bit 0 is set when the ordinary-flow subgroup result matches that reference.
- Bit 1 is set when the odd-invocation divergent-flow result matches, while even invocations set this bit directly because they do not enter that branch.
- Integer, Boolean, and floating min/max comparisons are exact. Floating add and multiply use source-defined tolerances that increase for subgroup size 128.
- For floating min/max, an empty-prefix identity based on positive or negative infinity is accepted through `identityOnly` because the compiler may assume those infinities do not occur in the program.
- The host requires every result to equal `0x3` through [`check()` and `checkComputeOrMesh()`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L2640-L2663). Any failed required-subgroup-size iteration fails the case.

## Behavior Parameter Identification

> **Behavior parameter:** `scan form`
>
> **Candidate values:** `reduction`, `inclusive scan`, `exclusive scan`

The operator changes the folded arithmetic or bitwise function, but scan form is the primary behavioral axis because it determines which invocations contribute to each invocation's expected result.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `reduction` | Incorrect all-active-set reduction, operator or type lowering, divergent active-set handling, or result transport/checking. |
| `inclusive scan` | Incorrect inclusion of the current invocation, prefix ordering or membership, operator or type lowering, divergent active-set handling, or result transport/checking. |
| `exclusive scan` | Incorrect exclusion of the current invocation, empty-prefix identity handling, prefix ordering or membership, operator or type lowering, divergent active-set handling, or result transport/checking. |

All three values also depend on correct stage support reporting, input binding, shader execution, and two-bit result readback.

## Important Variations and Special Cases

- Seven operators are registered: add, multiply, minimum, maximum, AND, OR, and XOR. Floating types omit bitwise operators; Boolean types omit non-bitwise operators.
- Scalar and vector forms cover signed and unsigned integers, floating-point types, doubles, and Booleans, including extended 8-bit and 16-bit types where supported. Vulkan SC omits the eight-component forms.
- `graphics`, `compute`, and `framebuffer` are always registered. `ray_tracing` and `mesh` are excluded from Vulkan SC builds.
- Compute and mesh add `_requiredsubgroupsize` cases. Mesh cases additionally select `mesh` or `task`; framebuffer cases select vertex, tessellation-control, tessellation-evaluation, or geometry stage.
- Ray-tracing format coverage comes from a smaller helper-provided list than the other stage families.
- The current default mustpass file contains 12,087 `subgroups.arithmetic` cases: 2,130 compute, 1,065 graphics, 4,260 framebuffer, 4,260 mesh, and 372 ray-tracing cases. No arithmetic-specific entry appears in `mustpass/main/src/test-issues.txt`.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Operation and scan enums | [`OpType`, `CaseDefinition`, and mapping helpers](../../../modules/vulkan/subgroups/vktSubgroupsArithmeticTests.cpp#L42-L150) | Defines the 21 scan/operator combinations and case state. |
| Reference shader body | [`getIndexVars()` and `getTestSrc()`](../../../modules/vulkan/subgroups/vktSubgroupsArithmeticTests.cpp#L179-L249) | Defines active-range selection, reference folding, comparisons, and result bits. |
| Operator helpers | [`getScanOpName()`, `getOpOperation()`, `getIdentity()`, and `getCompare()`](../../../modules/vulkan/subgroups/vktSubgroupsScanHelpers.cpp#L39-L349) | Expands exact built-in names, reference expressions, identities, and comparison tolerances. |
| Program construction | [`initFrameBufferPrograms()` and `initPrograms()`](../../../modules/vulkan/subgroups/vktSubgroupsArithmeticTests.cpp#L252-L277) | Selects common builders and SPIR-V targets. |
| Feature checks | [`supportedCheck()`](../../../modules/vulkan/subgroups/vktSubgroupsArithmeticTests.cpp#L279-L345) | Defines API, feature, type, stage, and subgroup-size gates. |
| Runtime dispatch | [`noSSBOtest()` and `test()`](../../../modules/vulkan/subgroups/vktSubgroupsArithmeticTests.cpp#L347-L468) | Routes cases to framebuffer, compute, graphics, ray-tracing, and mesh harnesses. |
| Registration | [`createSubgroupsArithmeticTests()`](../../../modules/vulkan/subgroups/vktSubgroupsArithmeticTests.cpp#L475-L665) | Generates the five direct intermediate nodes and their case matrices. |
| Common generated compute shader | [`initStdPrograms()` compute branch](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L1406-L1434) | Supplies descriptors, invocation indexing, and final result write. |
| Host result rule | [`check()` and `checkComputeOrMesh()`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L2640-L2663) | Requires `0x3` for every result element. |
| Mustpass evidence | [`vk-default/subgroups.txt`](../../../mustpass/main/vk-default/subgroups.txt#L1) | Lists executable `subgroups.arithmetic` paths. |
| Vulkan subgroup arithmetic semantics | [`shaders.adoc`](../../../../vulkan-docs/src/chapters/shaders.adoc#L3446-L3512) | Defines subgroup scope, reductions, scans, supported operators, and implementation-dependent order. |
| Vulkan feature meaning | [`limits.adoc`](../../../../vulkan-docs/src/chapters/limits.adoc#L1435-L1453) | Defines `VK_SUBGROUP_FEATURE_ARITHMETIC_BIT`. |

## Questions / Risk Points for User Audit

- The primary behavior parameter is fixed as scan form because it changes contributor membership. Operator remains a full matrix dimension rather than a competing primary axis.
- The representative walkthrough uses `compute.subgroupinclusiveadd_uint`, which exposes the inclusive boundary, the divergent second check, ordinary SSBO transport, and exact integer comparison without extended-type syntax.
- The result rule is source-grounded at `0x3`; stage-specific helpers only change how that value reaches host-visible storage.
- No unresolved source, mustpass, shader-target, or validation question changes the final page semantics.

## Conversion Notes for Final Wiki Rewrite

- Keep subgroup scope, scan boundaries, identities, active ballots, and implementation-dependent floating-point order as compact prerequisites.
- Use `dEQP-VK.subgroups.arithmetic.compute.subgroupinclusiveadd_uint` for the representative shader walkthrough, with `getTestSrc()` as the exact arithmetic-body builder and `initStdPrograms()` as the enclosing compute builder.
- Carry the scan-form behavior axis into `## Behavior Parameters`.
- Copy the `### Failure Cause Mapping` table exactly into the final page, then write fresh cause analysis grounded in the shader checks and Vulkan subgroup semantics.
- Move detailed helper and matrix navigation to the source appendix.
