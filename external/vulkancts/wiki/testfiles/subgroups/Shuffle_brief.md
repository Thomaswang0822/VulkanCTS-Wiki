# Understanding Brief: `subgroups.shuffle`

## One-Sentence Test Purpose

This test checks whether subgroup shuffle, relative shuffle, rotate, and clustered rotate operations return the value from the source invocation selected by each operation and argument form across supported shader stages and data types.

## Background Knowledge

### Subgroup data exchange

A subgroup operation lets shader invocations exchange values within one subgroup without storing those values in shared memory first. Shuffle operations select a source invocation by an absolute or relative rule. Rotate operations add wraparound, either across the whole subgroup or inside a fixed cluster.

Why it matters here:

- The returned value is defined by a source invocation index, not by an arithmetic transformation of the value itself.
- A source invocation may be inactive. The shader uses a ballot mask and checks results only when the computed source invocation is active and in range.

### Uniform and nonuniform operands

The operation selector can come from a per-invocation buffer element, one buffer element shared by every invocation, or a literal in the generated shader. These forms ask the compiler and implementation to handle the same family of operations with nonuniform, dynamically uniform, and constant operands.

Why it matters here:

- A dynamic selector can differ between invocations and is loaded from an SSBO.
- A dynamically uniform selector is loaded from one UBO element and has the same value for the subgroup.
- A constant selector is the literal `5` and needs no selector buffer read in the operation expression.

## One Concrete Example

For `dEQP-VK.subgroups.shuffle.compute.subgroupshufflexor_uint_dynamically_uniform`, every invocation reads `data2[0] % 32` as `id_in`, calls `subgroupShuffleXor(data1[gl_SubgroupInvocationID], id_in)`, and computes the expected source invocation as `gl_SubgroupInvocationID ^ id_in`. If that source invocation is active and in range, the returned value must equal `data1[id]`. Otherwise the shader records success because the operation result is not checked for an inactive source.

This example is the representative walkthrough because it exposes both the XOR source-index rule and the dynamically uniform argument path without the longer cluster-size loop used by clustered rotate.

## End-to-End Test Flow

```text
[host] choose the operation, argument form, data type, shader-stage family, and required-subgroup-size variant
[host] check subgroup operation, data type, shader-stage, and optional subgroup-size-control support
[host] generate GLSL through initPrograms or initFrameBufferPrograms with SPIR-V 1.3, or SPIR-V 1.4 for mesh and ray tracing
[host] initialize the value input and selector input with deterministic nonzero data
[host] create and bind result and input resources through the common subgroup harness
[host] dispatch, draw, trace rays, or run mesh work
[device] compute the selector and execute the selected shuffle or rotate operation
[device] derive the expected source invocation and compare the returned value when that source is active and in range
[device] write 1 for success and 0 for a checked mismatch
[host] wait, invalidate or copy back the result storage, and require every checked element to equal 1
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `getExtHeader()` enables the operation-specific GLSL subgroup extension, the ballot extension, and any extension required by the selected data format.
- `getNonClusteredTestSource()` emits the selector, operation call, expected source-index expression, ballot guard, and comparison for shuffle, XOR, up, down, and rotate.
- `getClusteredTestSource()` emits a loop over power-of-two cluster sizes and a compile-time-constant switch operand for clustered rotate.
- `initPrograms()` uses SPIR-V 1.3 for graphics and compute, and SPIR-V 1.4 for mesh and ray-tracing stages. `initFrameBufferPrograms()` uses SPIR-V 1.3.
- Compute, mesh, and task shaders use specialization constants for local size through `local_size_x_id`, `local_size_y_id`, and `local_size_z_id`.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Result SSBO or framebuffer output | yes | yes | written | yes | Stores one pass marker per tested invocation or rasterized result. |
| `data1` value buffer | yes | yes | read | no | Holds distinct deterministic input values so the selected source invocation can be checked. |
| Dynamic `data2` selector SSBO | yes | yes | read | no | Supplies one selector per subgroup invocation for the nonuniform argument form. |
| Dynamically uniform or constant-case `data2` UBO | yes | yes | read only for dynamically uniform cases | no | Supplies `data2[0]` for the dynamically uniform form. Constant cases still use the common resource setup but the generated operation uses literal `5`. |
| Subgroup ballot mask | no | no | created and read in the shader | no | Identifies active source invocations so undefined or unverifiable results do not cause a false failure. |

Framebuffer cases replace SSBO-based output with a color result and use UBO inputs because those paths intentionally avoid shader storage buffers. Graphics, ray-tracing, mesh, and compute paths otherwise use the common subgroup execution helpers.

## What Is Checked

- The shader computes the expected source invocation independently of the subgroup operation result.
- For an in-range active source, the returned value must equal the corresponding `data1` element.
- For an inactive or out-of-range source, the shader writes success without comparing the operation result.
- Clustered rotate repeats the comparison for every power-of-two cluster size from `1` through `gl_SubgroupSize` and combines all checks with bitwise AND.
- The host accepts a case only when every result element read by the selected harness equals `1`.
- Required-subgroup-size compute and mesh cases repeat the test for every supported power-of-two size from the device minimum through maximum and stop at the first failure.

## Behavior Parameter Identification

> **Behavior parameter:** operation family
>
> **Candidate values:** `shuffle`, `xor`, `up`, `down`, `rotate`, `clustered_rotate`
>
> **Secondary behavior parameter:** argument form
>
> **Candidate values:** `dynamic`, `dynamically_uniform`, `constant`

The operation family is the primary axis because it changes the rule that maps the current invocation to the expected source invocation. The argument form is a second behavioral axis because it changes whether the selector is nonuniform, dynamically uniform, or embedded as a literal, as well as the resource declaration used to obtain it.

## What Failure Means

### Failure Cause Mapping

Operation-family axis:

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `shuffle` | Incorrect absolute invocation selection or lowering of `subgroupShuffle`. |
| `xor` | Incorrect XOR-relative source selection or lowering of `subgroupShuffleXor`. |
| `up` | Incorrect subtraction-based source selection, boundary handling, or lowering of `subgroupShuffleUp`. |
| `down` | Incorrect addition-based source selection, boundary handling, or lowering of `subgroupShuffleDown`. |
| `rotate` | Incorrect modulo-subgroup wraparound or lowering of `subgroupRotate`. |
| `clustered_rotate` | Incorrect cluster partitioning, cluster-local wraparound, cluster-size handling, or lowering of `subgroupClusteredRotate`. |

Argument-form axis:

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `dynamic` | Incorrect handling of a per-invocation nonuniform selector or its SSBO load path. |
| `dynamically_uniform` | Incorrect handling of a runtime but subgroup-uniform selector or its UBO load path. |
| `constant` | Incorrect handling or optimization of the literal selector operand. |

Failures across all values can also come from shared stage plumbing, input initialization, descriptor access, result writes, synchronization, or host readback. The operation and argument patterns help separate those shared failures from operation-specific or operand-form-specific failures.

## Important Variations and Special Cases

- `shuffle` is generated only with `dynamic` selectors because its operand directly names an invocation. XOR, up, and down use all three argument forms.
- `rotate` and `clustered_rotate` use `dynamically_uniform` and `constant` selectors, but not `dynamic` selectors.
- Nonrotate dynamically uniform selectors use `data2[0] % 32`. Rotate selectors use a mask based on twice the subgroup size. Dynamic selectors use one element per invocation and mask by `gl_SubgroupSize - 1`.
- Clustered rotate tests every power-of-two cluster size. The cluster size is selected through a switch so each operation call has a pipeline-creation-time constant cluster operand.
- The full data-format matrix covers scalar and vector Boolean, signed integer, unsigned integer, floating-point, 8-bit, 16-bit, 64-bit, and long-vector forms where available. Ray tracing uses a smaller representative format list.
- The stage families are `graphics`, `compute`, `framebuffer`, `ray_tracing`, and `mesh`. Vulkan SC excludes rotate operations, ray tracing, mesh, and long-vector additions guarded by `CTS_USES_VULKANSC`.
- Framebuffer paths require 8-bit or 16-bit UBO storage support for corresponding narrow types. Compute and mesh required-size variants also require subgroup size control and full subgroup support.
- No `subgroups.shuffle` entry appears in `external/vulkancts/mustpass/main/src/test-issues.txt`, so no issue-list exclusion was found for this family.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Operation and argument definitions | [`OpType`, `ArgType`, and `CaseDefinition`](../../../modules/vulkan/subgroups/vktSubgroupsShuffleTests.cpp#L41-L72) | Defines the two behavior axes and support flags. |
| Operation names and extensions | [`getOpTypeName()` and `getExtensionForOpType()`](../../../modules/vulkan/subgroups/vktSubgroupsShuffleTests.cpp#L89-L141) | Maps each family to GLSL built-ins and extensions. |
| Resource declarations | [`getPerStageHeadDeclarations()`](../../../modules/vulkan/subgroups/vktSubgroupsShuffleTests.cpp#L143-L182) | Shows result, value, and selector bindings and the SSBO versus UBO choice. |
| Nonclustered shader logic | [`getNonClusteredTestSource()`](../../../modules/vulkan/subgroups/vktSubgroupsShuffleTests.cpp#L227-L270) | Defines selector forms, source-index formulas, active-lane guards, and comparisons. |
| Clustered rotate shader logic | [`getClusteredTestSource()`](../../../modules/vulkan/subgroups/vktSubgroupsShuffleTests.cpp#L273-L336) | Defines cluster-size iteration and cluster-local expected indices. |
| Shader builders | [`initFrameBufferPrograms()` and `initPrograms()`](../../../modules/vulkan/subgroups/vktSubgroupsShuffleTests.cpp#L350-L379) | Selects standard harness builders and SPIR-V targets. |
| Feature checks | [`supportedCheck()`](../../../modules/vulkan/subgroups/vktSubgroupsShuffleTests.cpp#L381-L483) | Gates operation features, formats, stages, narrow UBO types, and subgroup size control. |
| Resource setup and dispatch routing | [`noSSBOtest()` and `test()`](../../../modules/vulkan/subgroups/vktSubgroupsShuffleTests.cpp#L485-L654) | Shows input sizes, resource kinds, stage helpers, and required-size sweeps. |
| Registration matrix | [`createSubgroupsShuffleTests()`](../../../modules/vulkan/subgroups/vktSubgroupsShuffleTests.cpp#L661-L860) | Registers stage families, operation and argument combinations, formats, and suffixes. |
| Common compute shader builder | [`initStdPrograms()` compute branch](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L1406-L1434) | Wraps the generated body and writes one result per global invocation. |
| Deterministic input initialization | [`initializeMemory()`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L2293-L2407) | Fills bound input data and flushes host writes. |
| Host result checks | [`check()` and `checkComputeOrMesh()`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L2640-L2663) | Requires all scanned result values to equal the reference value. |
| Registered representative case | [`subgroups.txt`](../../../mustpass/main/vk-default/subgroups.txt#L39667) | Confirms the exact walkthrough path. |
| Vulkan subgroup operation semantics | [`shaders.adoc`](../../../../vulkan-docs/src/chapters/shaders.adoc#L3447-L3567) | Defines subgroup exchange, relative shuffle, rotate, and clustered rotate concepts. |
| Vulkan operation support bits | [`limits.adoc`](../../../../vulkan-docs/src/chapters/limits.adoc#L1428-L1480) | Connects operation classes to advertised subgroup capabilities. |

## Questions / Risk Points for User Audit

- Does the two-axis behavior model make clear that operation family controls source-index semantics while argument form controls operand uniformity and loading?
- Is the inactive-source rule clear enough to prevent interpreting every invocation as a checked data exchange?
- Are rotate and clustered rotate distinguished from up and down by wraparound and cluster partitioning?
- Is the shared harness boundary clear without hiding the operation-specific shader checks?

All semantic risk points above are resolved by the inspected source, mustpass entry, helper implementation, and Vulkan specification. No unresolved risk blocks conversion to the final page.

## Conversion Notes for Final Wiki Rewrite

- Use the XOR dynamically uniform compute case for the single representative shader walkthrough.
- Keep subgroup exchange, active invocation, and operand uniformity as short prerequisite bullets.
- Carry both behavior axes into `## Behavior Parameters`, including the operation and argument applicability matrix.
- Copy the `### Failure Cause Mapping` tables exactly into the final page.
- Keep helper and registration details in the source appendix unless they explain runtime checking or pruning.
