# Understanding Brief: cooperative_vector basic, longvec, matmul, and training

## One-Sentence Test Purpose

This test checks whether the `basic`, `longvec`, `matmul`, and `training` cooperative-vector families produce the expected vector or matrix values across their generated operations.

## Background Knowledge

### Cooperative vectors and long vectors

A cooperative vector is a shader vector type whose components can be evaluated together for small neural-network workloads. `VK_NV_cooperative_vector` exposes the `coopvecNV<T, N>` GLSL type and cooperative-vector load and store operations. The long-vector variant uses `GL_EXT_long_vector` and the `vector<T, N>` type. The two families exercise the same basic operation matrix, but they use different shader type and extension paths.

Why it matters here:
- The tested operation acts on a vector with a registered component count, while the host stores each invocation's vector in padded buffer space.
- Device support is combination-specific for NV cooperative vectors. The source queries advertised properties before it accepts a case. The long-vector path checks the EXT feature and maximum component count instead.

### Generated shader execution

The test generates one GLSL shader for the selected stage. A shader invocation loads its input vectors, applies the selected operation, and stores the result. Compute, graphics, mesh, tessellation, and ray-tracing stages use different invocation-index formulas, but the host checks the resulting vector values against a CPU reference.

Why it matters here:
- Storage class changes whether the shader accesses SSBO data directly, stages vectors through workgroup memory, or follows a buffer-reference path.
- Stage and storage choices affect support requirements and pruning, not the operation's mathematical reference.

## One Concrete Example

The registered case `dEQP-VK.cooperative_vector.basic.add.float16_float16.buffer.components1.compute` selects the `add` test family, equal FP16 input and output types, an SSBO, one component, and a compute shader. The generated shader uses `coopvecNV<float16_t, 1>`, loads `vecA` and `vecB` from bindings 0 and 1, evaluates `vecO = vecA + vecB`, and stores `vecO` to binding 3. The host compares the stored FP16 value with the reference sum.

The separate `matmul` family generates matrix multiply and multiply-add forms, while `training` generates `reducesum` and `outerproduct` forms. Both use their own matrix, layout, activation, storage, and stage dimensions in the same implementation file.

The `longvec` counterpart keeps the registered dimensions and changes the generated type to `vector<float16_t, 1>` while enabling `GL_EXT_long_vector`.

## End-to-End Test Flow

```text
[host] select a registered operation, component types, vector sizes, storage class, and shader stage
[host] check Vulkan version, extension features, limits, and advertised type combinations
[host] allocate four host-visible storage buffers for input A, input B, input C or bias, and output
[host] seed input data with deterministic random values and build the selected shader pipeline
[host] submit compute, graphics, mesh, tessellation, or ray-tracing work
[device] load vectors, execute the generated cooperative-vector operation, and store output values
[host] wait for completion, read the output buffer, and compute the matching CPU reference
[host] compare each output component and report pass or fail
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- The source builds GLSL in `CooperativeVectorTestCase::initPrograms`. It enables the common shader extensions, then selects `GL_NV_cooperative_vector` for `basic` or `GL_EXT_long_vector` for `longvec`.
- The shader uses specialization constants for local workgroup dimensions, matrix and layer offsets used by shared generator code, and the fragment width. Basic operation cases use the operation and vector dimensions to emit the selected expression.
- The representative basic case uses a compute shader and the source-controlled `spirv1.4` build option. The SPIR-V shown on the final page was compiled, validated, and disassembled from a reconstructed GLSL artifact with the local shader-disassembler toolchain.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Input A buffer | yes | yes, binding 0 | read | yes, for the reference | Supplies the first vector for each invocation. |
| Input B buffer | yes | yes, binding 1 | read | yes, for the reference | Supplies the second vector or operation input. |
| Input C or bias buffer | yes | yes, binding 2 when needed | read or used by selected variants | yes, when part of the reference | Supplies an auxiliary vector for load variants and matrix-related shared code. |
| Output buffer | yes | yes, binding 3 | written | yes | Carries the vector result back to the host. |
| Physical-address buffer | yes, only for `physical_buffer` | yes, binding 4 | read | yes | Holds four device addresses used by buffer-reference declarations. |
| Workgroup vectors | no separate host object | shader-local shared storage | read and written by compute invocations | no | Provides the workgroup storage path for `workgroup` and `workgroup_varptr`. |

## What Is Checked

- For integer basic cases, the host checks exact truncated integer results. The reference covers length, constants, conversion, composite construction and extraction, arithmetic, function negation, vector-times-scalar, and bit operations.
- For floating-point basic cases, the host computes the corresponding scalar reference for each component. Elementary functions and matrix-related paths use the tolerances and retry rules in the source.
- The host checks every invocation's output vector. A mismatch changes the final test result to fail and logs the selected vector dimensions; extended debug builds also dump the input, auxiliary, and output matrices.

## Behavior Parameter Identification

> **Behavior parameter:** test family
>
> **Candidate values:** `basic`, `longvec`, `matmul`, `training`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `basic` | Incorrect `VK_NV_cooperative_vector` type or operation lowering, unsupported advertised type combination accepted by the test, vector load/store addressing or padding error, stage or storage-class transport error, or host reference mismatch. |
| `longvec` | Incorrect `GL_EXT_long_vector` type or operation lowering, long-vector load/store or std140 layout error, stage or storage-class transport error, or host reference mismatch. |
| `matmul` | Incorrect cooperative-vector matrix operation lowering, matrix interpretation or layout handling, activation or transpose handling, matrix addressing, stage/storage transport, or host reference mismatch. |
| `training` | Incorrect training operation lowering, training-optimal layout handling, reduction or outer-product addressing, result-address/control-flow handling, stage/storage transport, or host reference mismatch. |

## Important Variations and Special Cases

- `basic` registers 29 operation families from `length` through `composite_array`. The source combines each with input/output type pairs, component counts, storage classes, and shader stages, then removes combinations that the operation or implementation cannot support. `matmul` and `training` are separate factory roots with their own operation and size tables.
- Both families register component counts `1`, `2`, `3`, `4`, `5`, `6`, `7`, `8`, `9`, `31`, `65`, and `1024`. Non-compute cases use reduced dimensions, and workgroup storage omits the largest vector because of shared-memory pressure.
- Integer types omit floating-point elementary functions and FMA. Floating-point types omit integer bitwise and shift operations. Conversion requires different input and output types; other non-matrix basic operations require matching types.
- `longvec` changes the shader representation and support gate. The source comment limits `useLongVector` to the basic operation matrix; the matrix multiply and training registrations use the NV path.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Category registration | [vktCooperativeVectorTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorTests.cpp#L37-L58) | Registers `basic`, `longvec`, `matmul`, and `training`; the first two use a shared factory and the latter two use separate factories. |
| Group and parameter matrix | [createCooperativeVectorBasicTests](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L3901-L4059) | Defines operation, type, size, storage, stage, and pruning dimensions. |
| Support checks | [CooperativeVectorTestCase::checkSupport](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L310-L483) | Selects NV property checks or the EXT long-vector feature and limit checks. |
| GLSL generation | [CooperativeVectorTestCase::initPrograms](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L564-L1750) | Emits extensions, resources, vector operations, stage code, and SPIR-V 1.4 build options. |
| Runtime setup | [CooperativeVectorTestInstance::iterate](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L1796-L2352) | Allocates buffers, fills inputs, builds descriptors, and prepares specialization data. |
| Result checking | [CooperativeVectorTestInstance::iterate](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L2791-L3896) | Computes references and compares output values. |
| Vulkan semantics | [Vulkan shader cooperative vectors](https://registry.khronos.org/vulkan/specs/latest/html/vkspec.html#shaders-cooperative-vector) | Defines cooperative-vector types, supported combinations, and operations. |

## Questions / Risk Points for User Audit

- Does the distinction between the `basic` NV path and the `longvec` EXT path remain clear when both families share the operation matrix?
- Is the host-visible buffer model clear for direct SSBO, workgroup, variable-pointer, and physical-buffer cases?
- Does the concrete one-component compute case explain the generated shader without implying that all registered cases use the same stage declarations?
- Are the pruning rules stated as source filters rather than as claims that the full Cartesian product runs?
- Does the failure mapping separate operation lowering and data transport from host reference or support-gate issues?

## Conversion Notes for Final Wiki Page

- Keep one page with `cooperative_vector` as the parser root and direct children `basic`, `longvec`, `matmul`, and `training`; place operation and generated axes in tables and prose.
- Distill the cooperative-vector versus long-vector explanation into short page-local prerequisite bullets.
- Use the one-component compute `add` case for the representative shader walkthrough. Preserve the source-generated operation and extension details, and keep the generated SPIR-V artifact collapsed.
- Copy the `### Failure Cause Mapping` table above directly into `## Failure Meaning` on the final page. Write `### Cause Analysis` separately for the final page.
