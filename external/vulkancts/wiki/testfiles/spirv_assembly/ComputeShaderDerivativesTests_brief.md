# Understanding Brief: spirv_assembly.instruction.compute.compute_shader_derivatives

## One-Sentence Test Purpose

This test checks whether an implementation that advertises `VK_KHR_compute_shader_derivatives` (and, for the mesh/task paths, `VK_EXT_mesh_shader` with `meshAndTaskShaderDerivatives`) correctly executes SPIR-V derivative, quad subgroup, and LOD instructions inside `GLCompute`, `MeshEXT`, and `TaskEXT` entry points under the `DerivativeGroupLinearKHR` and `DerivativeGroupQuadsKHR` execution modes.

## Background Knowledge

### Compute-shader derivatives (`VK_KHR_compute_shader_derivatives` / `SPV_KHR_compute_shader_derivatives`)

The Vulkan fragment-shader pipeline computes derivatives (`dFdx`, `dFdy`, `fwidth`) implicitly per 2×2 pixel quad. Compute, mesh, and task shaders have no rasterizer, so the SPIR-V extension defines two explicit execution modes that group invocations into the units derivatives are computed over:

- `DerivativeGroupLinearKHR` — groups 4 consecutive invocations in the linear `LocalInvocationIndex` order. The host enables it with the `ComputeDerivativeGroupLinearKHR` capability and the `computeDerivativeGroupLinear` feature bit. The test exercises it with `(16,1,1)` and `(4,4,1)` workgroups.
- `DerivativeGroupQuadsKHR` — groups 2×2 invocations by `(x,y)` index. Requires `ComputeDerivativeGroupQuadsKHR` and `computeDerivativeGroupQuads`. The test uses `(4,4,1)` workgroups only.

The two modes differ in which invocations share a derivative quad, so the same input pattern produces different expected derivative values. SPIR-V `OpDPdx`/`OpDPdy`/`OpFwidth` (and the `*Fine`/`*Coarse` variants) become legal inside these compute-like entry points only when the corresponding execution mode is set.

Why it matters here:
- The test family is built around the `DerivativeGroupLinearKHR` vs `DerivativeGroupQuadsKHR` split. Every test case picks one mode, and the host-side expected buffer is generated differently for each.
- For `LINEAR`, derivatives are taken along the X axis over 4 consecutive invocations; the test value depends on `ndx & 3`. For `QUADS`, derivatives are taken along X and Y over a 2×2 quad; the test value depends on `ndx & 1` and `ndy & 1`.

### Mesh and task shader derivatives

`VK_EXT_mesh_shader` adds the `MeshEXT` and `TaskEXT` execution models. Derivative operations are not automatically legal in those stages; the implementation must also report `meshAndTaskShaderDerivatives` VK_TRUE in `VkPhysicalDeviceComputeShaderDerivativesPropertiesKHR`. The mesh/task variants of every case register only when that property is supported, and they additionally require `meshShader` (mesh) or both `meshShader` and `taskShader` (task) features.

Why it matters here:
- The mesh and task shader templates are nearly identical to the compute template apart from `OpEntryPoint`, `OpExecutionMode` (mesh adds `OutputVertices 3`, `OutputPrimitivesEXT 1`, `OutputTrianglesEXT`), and a trailing block that emits mesh output (`OpSetMeshOutputsEXT` + vertex/index stores for mesh; `OpEmitMeshTasksEXT` for task).
- The task path pairs the task shader with a fixed mesh shader that draws a single triangle, and the mesh path pairs the mesh shader with a fixed fragment shader. The host reads results back from the storage buffers; the rendered image is not the test signal.

### Subgroup operations and quad swap semantics

`OpGroupNonUniformQuadBroadcast` and `OpGroupNonUniformQuadSwap` operate on a 4-invocation quad. The test maps `quadNdx` 0..3 (broadcast) or 0..2 (swap Horizontal/Vertical/Diagonal) to expected permutations of the input values across the quad. `verify_ndx` writes `SubgroupLocalInvocationId % 4` to confirm that the quad grouping seen by `OpSubgroup*` matches the grouping the derivative mode implies.

Why it matters here:
- `verify_ndx` and `quad_op` require Vulkan 1.1+ and `VK_SUBGROUP_FEATURE_BASIC_BIT` (plus `VK_SUBGROUP_FEATURE_QUAD_BIT` for `quad_op`). They are skipped on devices that do not report quad support in the relevant shader stage.
- `verify_ndx` additionally requires `numWorkgroup.x() % subgroupSize == 0` (VUID-VkPipelineShaderStageCreateInfo-flags-02759) and sets `VK_PIPELINE_SHADER_STAGE_CREATE_REQUIRE_FULL_SUBGROUPS_BIT` on the compute pipeline.

## One Concrete Example

Take `compute.derivative_value.normal.float32.linear.16_1_1`. The SPIR-V module is a `GLCompute` shader with `LocalSize 16 1 1` and `DerivativeGroupLinearKHR`. Each invocation reads `LocalInvocationID.x` (0..15), masks it down to `ndx & 3`, multiplies by 10 to form `%test_value`, then computes `%dx = OpDPdx %test_value`, `%dy = OpDPdy %test_value`, and `%fwidth = OpFwidth %test_value`. The three results are stored at `out_x_var[0][ndx]`, `out_y_var[0][ndx]`, and `out_f_var[0][ndx]` respectively. The host dispatches `(1,1,1)` workgroups of local size `(16,1,1)`, reads back the three output buffers, and compares them against precomputed vectors where `expX[ndx]=10`, `expY[ndx]=20`, `expF[ndx]=30` (the linear normal-variant derivative of `10 * (ndx & 3)` is 10 in x, 20 in y, 30 in width). The comparison is exact (no tolerance for the `derivative_value` cases).

This is the simplest case; `vec2/3/4_float32` repeats the same pattern with composite `test_value` construction, `fine`/`coarse` change the `OpDPdx*` opcode, `quads` switches the execution mode and the masking, and `mesh`/`task` swap the entry point.

## End-to-End Test Flow

```text
[host] checkSupport: require VK_KHR_compute_shader_derivatives; require computeDerivativeGroupLinear or computeDerivativeGroupQuads; for mesh/task require VK_EXT_mesh_shader, meshAndTaskShaderDerivatives, meshShader/taskShader; for verify_ndx/quad_op require Vulkan 1.1 + subgroup basic/quad bits in the relevant stage; for verify_ndx require numWorkgroup.x() % subgroupSize == 0
[host] initPrograms: build SPIR-V assembly via tcu::StringTemplate from the per-shaderType template (compute / mesh / task) specialized by per-testType specMap (capability, executionMode, testValueCode, testLogicCode, storeCode, arrayDeclaration, dataType, decorations, images)
[host] create 4 storage buffers (bindings 0..3), 1 sampled image+view+sampler (binding 4), descriptor set layout, pipeline layout, descriptor set; for mesh/task also create render target, render pass, framebuffer, fixed fragment shader (mesh/task) and fixed mesh shader (task)
[host] record command buffer: clear all 4 buffers to 0; clear sampled image mip 0/1 to CLR_COLORS[0]/[1]; transition sampled image to SHADER_READ_ONLY_OPTIMAL; bind pipeline and descriptor set; dispatch (compute) or cmdDrawMeshTasksEXT 1,1,1 (mesh/task); insert buffer barriers to HOST_READ
[host] submitCommandsAndWait
[device] each invocation: compute ndx/ndy, mask to local quad coordinates, build %test_value (varies by testType), execute the tested SPIR-V instruction(s), store result(s) into the output SSBO(s)
[host] checkResult: build expected buffer(s) on the CPU from the same per-testType/feature/variant/dataType rules; compare against the readback buffers; for LOD_QUERY use compareFloats with a tolerance derived from the [lodMin, lodMax] range; for all other testTypes use exact equality
[host] pass if every element matches, else fail with per-element diagnostic
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- One **per-shader-type SPIR-V assembly template** for the test shader: `ShaderType::COMPUTE` (lines 3071-3184), `ShaderType::MESH` (lines 3191-3350), `ShaderType::TASK` (lines 3357-3471). Each template carries `${capability}`, `${executionMode}`, `${testValueCode:opt}`, `${testLogicCode}`, `${storeCode}`, `${linearNdxMul}`, `${arrayDeclaration}`, `${arrayStride}`, `${dataType}`, `${decorations:opt}`, `${images:opt}`, `${sampleCap:opt}`, `${queryCap:opt}`, `${interface:opt}` placeholders that are filled in two `tcu::StringTemplate` passes per test type.
- One **fixed mesh shader** (`meshShaderStr`, lines 2912-3001) used only by the `task` shader-type path. It draws a single triangle (3 vertices, 1 primitive) and does not participate in the tested derivative behavior.
- One **fixed fragment shader** (`fragmentShaderStr`, lines 3003-3034) used by `mesh` and `task` paths. It writes a constant red output; the rendered image is not the test signal.
- The SPIR-V target version is **1.3 for compute and fragment shaders**, **1.4 for mesh and task shaders** (lines 3682, 3691, 3695, 3704, 3708-3709).

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| `out_x_var` (SSBO, binding 0) | yes; host-cleared to 0; sized to `numWorkgroup.x*y*z * alignedSize(dataType)` (or `*4` for verify_ndx) | yes (descriptor set 0 binding 0) | yes — shader writes `dx` (derivative_value), `subgroup_val` (verify_ndx), `store_value` (quad_op), or `store_value` (lod_sample/query) | yes — host compares against expected | Primary output channel for every test type. |
| `out_y_var` (SSBO, binding 1) | yes; same shape as `out_x_var` | yes (binding 1) | yes — shader writes `dy` (derivative_value) or `invocation_val` (verify_ndx) | yes — host compares | Secondary output for derivative_value (dy) and verify_ndx (invocation id). Unused (but still bound and cleared) for quad_op and lod_op. |
| `out_f_var` (SSBO, binding 2) | yes; same shape as `out_x_var` | yes (binding 2) | yes — shader writes `fwidth` (derivative_value only) | yes — host compares | Tertiary output for derivative_value fwidth. Unused (but still bound and cleared) for verify_ndx, quad_op, lod_op. |
| 4th SSBO (binding 3) | yes; allocated and cleared | yes (binding 3) | no — never written by the shader | yes — allocated for symmetry | Placeholder slot; descriptor layout always allocates 4 SSBOs and a combined image sampler, even when only 1-3 are used. |
| Sampled image+view+sampler (binding 4) | yes; 2 mip levels (1D for LINEAR, 2D for QUADS); `VK_FORMAT_R32G32B32A32_SFLOAT`; nearest filtering, clamp-to-edge | yes (binding 4) | yes — read by `OpImageSampleImplicitLod` (lod_sample) or `OpImageQueryLod` (lod_query) | no | Only lod_op cases read it. Mip 0 is filled with `(0.5,0.5,0.5,0.5)` and mip 1 with `(1.0,1.0,1.0,1.0)`. |
| Render target image+view (mesh/task only) | yes; `VK_FORMAT_R8G8B8A8_UNORM`, 32×64 | yes (color attachment) | yes — fragment shader writes constant color | no | Drives the graphics pipeline so mesh/task shaders run; not the test signal. |

## What Is Checked

- **derivative_value**: host builds three expected vectors (`expX`, `expY`, `expF`) of length `numWorkgroup.x*y*z * alignedComponentCount(dataType)`. For non-FINE variants, every element is `(10, 20, 30)` (with `0` for the 4th component of `vec3_float32` due to vec3 padding). For FINE variants, expected values differ per `ndx % 4` or `ndx % 8` depending on `LINEAR`/`QUADS` and `dataType`. Comparison is exact (no tolerance).
- **verify_ndx**: host builds one expected `uint32` vector where `expI[ndx] = ndx % 4` (LINEAR) or a 2×2 pattern (QUADS). Also verifies that all 4 invocations of each quad share the same `gl_SubgroupID` value (each quad must live in one subgroup). Comparison is exact.
- **quad_op**: host builds one expected `float` vector. For BROADCAST, `exp0[ndx] = 10 * quadNdx`. For SWAP, `exp0` is built by `getHorizontallySwappedValues` / `getVerticallySwappedValues` / `getDiagonallySwappedValues` depending on `quadNdx` (0/1/2 → Horizontal/Vertical/Diagonal). Comparison is exact.
- **lod_sample**: host builds one expected `vec4` vector where every 4-element group is `CLR_COLORS[mipLvl]` (the same color used to clear the sampled mip). Comparison is exact.
- **lod_query**: host computes the LOD range `[lodMin, lodMax]` from `feature` and `mipLvl`, then expects `out0[ndx] = mipLvl` for even `ndx` and `out0[ndx] = (lodMin+lodMax)/2` for odd `ndx`. The even slot (integer mip level) is compared exactly; the odd slot (computed LOD) is compared with `compareFloats(a, b, 0.015 + (lodMax-lodMin)/2)`.
- All comparisons log per-element `got:`/`expected:` diagnostics to the test log on mismatch; the case returns `pass` only if every element matches.

## Behavior Parameter Identification

> **Behavior parameter:** `testType` (intermediate node below `<shaderType>`), with `shaderType` as a secondary axis (intermediate node below `compute_shader_derivatives`).
>
> **Candidate values:**
> - `testType` ∈ {`derivative_value`, `verify_ndx`, `quad_op`, `lod_op` (split into `sample`/`query`)}
> - `shaderType` ∈ {`compute`, `mesh`, `task`}
> - secondary: `feature` ∈ {`linear`, `quads`}; `variant` ∈ {`normal`, `fine`, `coarse`} (derivative_value only); `dataType` ∈ {`float32`, `vec2_float32`, `vec3_float32`, `vec4_float32`}; `quadOp` ∈ {`broadcast`, `swap`}; `quadNdx` ∈ {0..3 (broadcast), 0..2 (swap)}; `numWorkgroup` ∈ {(16,1,1), (4,4,1), (128,1,1), (32,4,1)}; `mipLvl` ∈ {0, 1}; `useLocalInvocationIndex` ∈ {false, true} (quads variant of derivative_value only).

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `derivative_value` (any variant/feature/dataType) | Derivative instruction returns wrong value; derivative group execution mode not honored; per-quad invocation grouping incorrect. |
| `verify_ndx` | `gl_SubgroupInvocationID` does not match the per-quad index implied by the derivative group mode; quad invocations split across subgroups. |
| `quad_op` (broadcast) | `OpGroupNonUniformQuadBroadcast` reads the wrong lane or the quad layout differs from the assumed 2×2 / 4-linear grouping. |
| `quad_op` (swap) | `OpGroupNonUniformQuadSwap` Horizontal/Vertical/Diagonal mapping is wrong relative to the derivative group layout. |
| `lod_op` (sample) | `OpImageSampleImplicitLod` computes the wrong LOD from compute-shader derivatives; mip-level data layout or addressing is wrong. |
| `lod_op` (query) | `OpImageQueryLod` returns a LOD outside the spec-derived `[lodMin, lodMax]` range or the integer mip level is wrong. |
| Any `mesh` or `task` case | Same as the corresponding `compute` case, but specifically when mesh/task shader derivative support is broken; or the mesh/task shader did not actually run (render-target / mesh output setup is wrong). |

### Cause Analysis (placeholder — written fresh in the final page)

Detailed per-cause analysis is deferred to `## Failure Meaning` → `### Cause Analysis` in the final Level-3 page. The brief only enumerates the cause names that the table above maps.

## Important Variations and Special Cases

- **`useLocalInvocationIndex` (quads variant of derivative_value only)**: a second `4_4_1_local_inv_index` case is registered for every `(variant, dataType)` pair under `quads`. It switches the shader from reading `LocalInvocationID.x/.y` to reading `LocalInvocationIndex` and deriving `ndx = inv_index % wg_size_x`, `ndy = (inv_index / wg_size_x) % wg_size_y`. The two paths exercise different addressing modes for the same quad layout. The host-side expected values are identical.
- **`vec3_float32` padding**: `OpTypeVector %float32 3` is declared with `ArrayStride 16` (vec3 is aligned to vec4 in std430). The test writes 0 into the 4th component and the host-side expected vector also writes 0 at `(ndx+1) % 4 == 0`.
- **Workgroup X for `verify_ndx`**: must be a multiple of `subgroupSize` (VUID-VkPipelineShaderStageCreateInfo-flags-02759). The compute pipeline sets `VK_PIPELINE_SHADER_STAGE_CREATE_REQUIRE_FULL_SUBGROUPS_BIT` for `verify_ndx` (and only for `verify_ndx`).
- **Sampled image geometry**: `LINEAR` lod_op cases use a 1D image (`SAMPLED_EXTENT_1D = {16,1,1}`) and require `OpCapability Sampled1D`; `QUADS` lod_op cases use a 2D image (`SAMPLED_EXTENT_2D = {4,4,1}`) and add no extra capability.
- **Non-VulkanSC only**: the entire `compute_shader_derivatives` family is registered only when `CTS_USES_VULKANSC` is not defined (the source file is excluded from VulkanSC builds).
- **Two-pass `tcu::StringTemplate` specialization**: the test shader is specialized in two passes because `testLogicCode` and `storeCode` themselves contain `${dxFunc}`/`${dyFunc}`/`${dwidthFunc}`/`${quadOp}`/`${quadNdx}`/`${storeNdx}` placeholders that depend on the second-level specMap. A reader who greps the assembly must apply both passes to recover the final text.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Test case class and `checkSupport` | [`ComputeShaderDerivativeCase::checkSupport`](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderDerivativesTests.cpp#L2830-L2907) | Feature/property/subgroup gating logic for every test case. |
| Test instance `iterate` | [`ComputeShaderDerivativeInstance::iterate`](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderDerivativesTests.cpp#L2415-L2822) | Host-side command buffer recording, dispatch/draw, and result check entry. |
| Compute shader template | [`ShaderType::COMPUTE` block in `initPrograms`](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderDerivativesTests.cpp#L3068-L3187) | The SPIR-V assembly string template for the compute variant. |
| Mesh shader template | [`ShaderType::MESH` block in `initPrograms`](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderDerivativesTests.cpp#L3188-L3353) | The SPIR-V assembly string template for the mesh variant. |
| Task shader template | [`ShaderType::TASK` block in `initPrograms`](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderDerivativesTests.cpp#L3354-L3477) | The SPIR-V assembly string template for the task variant. |
| Fixed mesh shader (task path) | [`meshShaderStr`](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderDerivativesTests.cpp#L2912-L3001) | The fixed mesh shader that draws one triangle for the task path. |
| Fixed fragment shader (mesh/task path) | [`fragmentShaderStr`](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderDerivativesTests.cpp#L3003-L3034) | The fixed fragment shader paired with mesh/task test shaders. |
| `derivative_value` specialization | [`TestType::DERIVATIVE_VALUE` block`](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderDerivativesTests.cpp#L3482-L3521) | First and second specMap for derivative_value cases. |
| `verify_ndx` specialization | [`TestType::VERIFY_NDX` block`](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderDerivativesTests.cpp#L3522-L3556) | specMap for verify_ndx cases (subgroup id and invocation id stores). |
| `quad_op` specialization | [`TestType::QUAD_OPERATIONS` block`](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderDerivativesTests.cpp#L3557-L3588) | specMap for quad_op cases. |
| `lod_sample` specialization | [`TestType::LOD_SAMPLE` block`](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderDerivativesTests.cpp#L3589-L3629) | specMap for lod_op.sample cases. |
| `lod_query` specialization | [`TestType::LOD_QUERY` block`](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderDerivativesTests.cpp#L3630-L3671) | specMap for lod_op.query cases. |
| Result verification | [`ComputeShaderDerivativeInstance::checkResult`](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderDerivativesTests.cpp#L1842-L2413) | Per-testType expected-value generation and comparison logic. |
| Test value generator (derivative_value) | [`getTestValueCode`](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderDerivativesTests.cpp#L345-L424) | Builds the per-feature/variant/dataType SPIR-V fragment that computes `%test_value`. |
| Texture coordinate generator (lod_op) | [`genTexCoords`](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderDerivativesTests.cpp#L489-L518) | Builds the per-feature/mipLvl SPIR-V fragment that computes texture coordinates. |
| Swap-value generators (quad_op swap) | [`getHorizontallySwappedValues` / `getVerticallySwappedValues` / `getDiagonallySwappedValues`](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderDerivativesTests.cpp#L621-L1123) | Host-side expected buffers for the three swap directions. |
| Registration root | [`createComputeShaderDerivativesTests`](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderDerivativesTests.cpp#L3729-L4176) | Builds the `compute_shader_derivatives` group and all leaves. |
| Mustpass listing | [`spirv-assembly.txt`](../../../mustpass/main/vk-default/spirv-assembly.txt) | All test case leaves registered in the default mustpass. |

## Questions / Risk Points for User Audit

- Is the primary behavioral axis correctly identified as `testType` (with `shaderType` as a secondary axis), or should `shaderType` be treated as the primary axis instead?
- Are the 5 `testType` values (`derivative_value`, `verify_ndx`, `quad_op` / broadcast+swap, `lod_op` / sample+query) the right grouping for `## Behavior Parameters` subsections, or should `lod_op.sample` and `lod_op.query` be separate subsections?
- Is one representative walkthrough (`compute.derivative_value.normal.float32.linear.16_1_1`) sufficient, or should a second walkthrough cover `compute.quad_op.broadcast.float32.quads.4_4_1.0` to show the QUADS execution mode and `OpGroupNonUniformQuadBroadcast`?
- Is the `out_z`/4th-binding placeholder slot (always allocated, never written by the shader) worth calling out in `## Runtime Execution`, or is it noise?
- For `lod_query`, the spec-derived `[lodMin, lodMax]` range and the `0.015 + (lodMax-lodMin)/2` tolerance are taken verbatim from the source comments. Are these correctly attributed as the test's own tolerance, not a Vulkan spec tolerance?

## Conversion Notes for Final Wiki Rewrite

- Distill `Background Knowledge` into 3 bullets: compute-shader derivative execution modes; mesh/task shader derivative property gate; subgroup/quad operation requirements for `verify_ndx`/`quad_op`. Drop the fine-grained per-mode explanations; the `## Behavior Parameters` subsections will repeat the relevant detail where it changes behavior.
- Use one representative shader walkthrough: `compute.derivative_value.normal.float32.linear.16_1_1`. Per the `TEMP-SPIRV-ASSEMBLY` deviation, extract the specialized SPIR-V assembly from the C++ string templates and place it under `#### Source Code` (unfoldable, `;`-annotated). Omit `#### SPIR-V` subsection. Run `spirv-as` → `spirv-val` → `spirv-dis` as a generation-time validation gate against `spirv1.3`; do not publish the disassembler output.
- Carry `### Failure Cause Mapping` table directly into the final page; write `### Cause Analysis` fresh.
- Move the source-link heavy parts into `## Source Reference Appendix` as a compact table; keep only the most navigation-critical links inline.
- The two-pass `tcu::StringTemplate` specialization is a non-obvious reconstruction detail; mention it once in `## Shader Analysis` so a reader who greps the C++ source understands why a single `specialize` call is not enough.
- The fixed mesh shader / fixed fragment shader paired with mesh/task paths are not the test signal; mention them in `## Runtime Execution` only as infrastructure that lets the test shader run.
- The 4th-binding placeholder slot is a minor implementation detail; mention it once in `## Runtime Execution` to explain why bindings 0..3 are always allocated even when only 1-3 are written.
