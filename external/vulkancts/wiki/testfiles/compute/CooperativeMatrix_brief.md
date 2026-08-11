# Understanding Brief: cooperative_matrix / vktComputeCooperativeMatrixTests.cpp

## One-Sentence Test Purpose

This test checks whether an implementation correctly compiles and executes compute-shader cooperative matrix operations, conversions, reductions, tensor-layout addressing, clamp addressing, multicomponent loads/stores, and 64-bit indexing, across the NV and KHR cooperative-matrix use types, scopes, subgroup-size modes, component types, storage classes, layouts, and address methods.

## Background Knowledge

### What a cooperative matrix is

A cooperative matrix is a matrix value whose individual elements are distributed across the invocations of a single Vulkan scope (subgroup or workgroup). Each invocation holds a slice of the matrix; the operations `coopMatLoad`, `coopMatStore`, `coopMatMulAdd`, `coopMatTransposeNV`, `OpCooperativeMatrixReduceNV`, and `coopMatLoadTensorNV` then collectively perform the matrix-wide computation as if it were a normal variable. The matrix has a declared `scope`, `M`, `N`, optional `K`, an element component type, and a **use** that tells the SPIR-V / GLSL type system which operand role the matrix fills in larger expressions:

- `gl_MatrixUseA` — operand A of a multiply
- `gl_MatrixUseB` — operand B
- `gl_MatrixUseAccumulator` — accumulator/C/Result matrix

The use is part of the matrix type. Assigning a matrix of one use to a matrix of a different use is a SPIR-V / GLSL type error. The CTS code uses `UT_NV`, `UT_KHR_A`, `UT_KHR_B`, `UT_KHR_C`, and `UT_KHR_Result` to enumerate these uses; `UT_KHR_C` only changes the test generation because matrix C cannot be used as an arithmetic operand in most tests.

Why it matters here:

- The same operation (for example `matO = matA + matB`) compiles only when each matrix is constructed with a compatible use type.
- NV cooperative matrices use a different syntax (`fcoopmatNV<32, gl_ScopeSubgroup, 16, 8>`); KHR matrices use `coopmat<float, gl_ScopeSubgroup, 16, 8, gl_MatrixUseA>`. The two branches `nv` and `khr_*` therefore generate different shaders with different use-type declarations.

### Scope and use-type interaction

`scopeCases` enumerates `subgroupscope` (default for both NV and KHR) and `workgroupscope` (KHR-only; `vkWorkgroupScope` is gated behind `cooperativeMatrixWorkgroupScope`). For workgroup-scope matrices, the generator emits `shared matA[]`/`sharedB`/`sharedC` arrays sized by the number of subgroups in the workgroup, copies inputs from a uniform-binding SSBO into shared memory once, then performs a workgroup reduction inside `main`.

The combination of scope and use produces the per-leaf groups: `khr_a.subgroupscope`, `khr_a.workgroupscope`, `khr_r.subgroupscope`, etc. The shader-facing binding layout (binding 0 = A, binding 1 = B, binding 2 = C, binding 3 = output) is identical across these scope variants.

### Address method, layout, and storage class

| Variant | What it changes |
|---|---|
| `linear` (`ADDR_LINEAR`) | `coopMatLoad`/`coopMatStore` with an explicit stride and row/column-major flag. Default for almost every test. |
| `tensorlayout` (`ADDR_TENSORLAYOUT`) | `createTensorLayoutNV` + `coopMatLoadTensorNV`; the test matrix dims become tensor dimensions and the generated shader uses `sliceTensorLayoutNV` to address the matrix. Requires `cooperativeMatrixTensorAddressing`. |
| `blocksize` (`ADDR_BLOCKSIZE`) | Adds `setTensorLayoutBlockSizeNV` to express block-quantized layout. Requires `cooperativeMatrixBlockLoads`. |
| `decode` (`ADDR_DECODE`) | Combines block layout with a `decodeFunc` callback for dequantization. Used by `TT_MATRIXMULADD_DEQUANT`. |

Storage class `scCases` controls where the A/B/C buffers live: SSBO (`buffer`), workgroup-shared (`workgroup`), SSBO with variable pointers (`buffer_varptr`, needs `variablePointers`), workgroup with variable pointers (`workgroup_varptr`), or physical storage buffer (`physical_buffer`, needs `bufferDeviceAddress`). For `physical_buffer` the four input/output buffers are placed behind binding 4 as a `Params` struct containing buffer-reference addresses, rather than at bindings 0–3 directly.

Colmajor/rowmajor (`colCases`) is a bool flag passed into `coopMatLoad`/`coopMatStore` and affects the host-side reference calculation.

### Subgroup-size mode

`SUBGROUP_SIZE_NONE` lets the shader pick whatever subgroup size the device reports. The `_min` and `_max` modes pass `gl_SubgroupSize` to the GLSL shader and require `cooperativeMatrixFlexibleDimensions` to find M/N/K granularities that work at the extreme sizes. `SUBGROUP_SIZE_MIN`/`SUBGROUP_SIZE_MAX` are only generated for `TT_MATRIXMULADD` because that test type's M/N/K dimensions actually depend on subgroup size; all other test types skip subgroup-size modes.

### Component types and arithmetic properties

`dtCases` lists the `inputType / outputType` combinations the shader exercises. Some are NV-only (`float16_float16`, `sint32_sint32`, etc.), some are non-VulkanSC only (`bfloat16_*`, `floate5m2_*`, `floate4m3_*`), and a few mix signed/unsigned in the MMA case (`sint8_sint32`, `uint8_sint32`) to test signedness conversion rules. The 64-bit component types (`sint64`, `uint64`, `float64`) are intentionally not part of the standard `dtCases` matrix; they are still present in the explicit `convert`/`multicomponent` matrices because conversions between narrower and wider types are tested separately.

Why it matters here:

- Some component types cannot be combined in the same matrix multiply. `TT_MATRIXMULADD` rejects matrices where the input-type bit width is larger than the output-type bit width, and rejects signedness mixing for `UT_NV`.
- Bfloat16 / E5M2 / E4M3 component types force KHR use types (`UT_KHR_A`, `UT_KHR_B`, `UT_KHR_Result`); they cannot be combined with `UT_NV`.

### Test types (operation types)

`ttCases` enumerates the operations under test. The full enumeration includes:

- **Constructor / length**: `length`, `constant` (`OpConstantComposite`), `composite` (`OpCompositeConstruct`), `composite_rvalue` (`OpCompositeExtract`).
- **Arithmetic**: `add`, `sub`, `div`, `mul`, `negate`, `matrixtimesscalar` (`OpMatrixTimesScalar`).
- **Function calling**: `func` (pass by pointer), `func_const_in` (pass by value).
- **Matrix multiply**: `matrixmuladd`, `matrixmuladd_array`, `matrixmuladd_saturated`, `matrixmuladd_wrapping`, `matrixmuladd_stride0`, `matrixmuladd_cross`, `matrixmuladd_dequant`, `matrixmuladd_push` (push-constant stride).
- **Convert / transpose**: `convert_acc_to_a`, `convert_acc_to_b`, `transpose_acc_to_b`, plus separate `convert` / `convert_sat` matrices outside `ttCases`.
- **Reduce**: `reduce_sum_row`, `reduce_sum_col`, `reduce_sum_rowcol`, `reduce_sum_2x2`, plus `_min_` variants and `_changedim` variants that change the output dimensions.
- **Per-element operations**: `per_element_op`, `per_element_op_row_col`, `per_element_op_struct`, `per_element_op_mat` (`OpCooperativeMatrixPerElementOpNV` / `GL_NV_cooperative_matrix2`).
- **Tensor layout**: `tensorlayout1d` … `tensorlayout5d`, plus `_clip` variants (with `setTensorLayoutClampValueNV`), plus `spacetodepth`.
- **Clamp addressing**: `clampconstant`, `clamptoedge`, `clamprepeat`, `clampmirrorrepeat`.
- **Multicomponent** (separate branch outside `ttCases`): `multicomponent.load` and `multicomponent.save`, using `vec2`/`vec4` source or destination types.

Why it matters here:

- `ttCases` controls which SPIR-V op (or which GLSL builtin) the shader emits. Each operation has its own GLSL shape and its own host-side reference formula.
- The `convert` and `multicomponent` branches live outside `ttCases` because they iterate over a different cartesian product (input × output component type, with optional saturation or vector count) rather than a single component-type pair.
- The result matrix is `matO`. The shader's host-side check compares `matO` against the expected reference for the chosen operation, with the comparison rule chosen by `testType` (epsilon for float, mask for integer, sum/min/identity for reduce, etc.).

### 64-bit indexing (non-VulkanSC only)

The `64b_indexing` subtree is structurally separate from the GLSL-generated matrix. It uses handwritten GLSL (not the regular generator), targets SPIR-V 1.6, requires `VK_PIPELINE_CREATE_2_64_BIT_INDEXING_BIT_EXT`, and combines a 2 GiB input buffer with one of three offsets:

| Sub-leaf | Layout | Offset (bytes) |
|---|---|---|
| `coopmat_64b_rowmajor` | row-major | 1536 |
| `coopmat_64b_rowmajor_mediumoffset` | row-major | 1 GiB |
| `coopmat_64b_rowmajor_largeoffset` | row-major | 5 GiB |
| `coopmat_64b_tensorlayout` | tensor layout | 1536 |
| `coopmat_64b_tensorlayout_mediumoffset` | tensor layout | 1 GiB |
| `coopmat_64b_tensorlayout_largeoffset` | tensor layout | 5 GiB |

The shader loads a `coopmat<int32_t, gl_ScopeSubgroup, M, N, gl_MatrixUseAccumulator>` (M = N = 16) at the pushed offset, bitwise-complements every element, and stores the matrix back to the same offset. The reference calculation on the host inverts the same operation and checks each buffer element. Elements outside the matrix window are unchanged.

### Delegated `op_constant_null`

The `op_constant_null` subtree is registered through `vktComputeCooperativeMatrixOpConstantNullTests.cpp` via `createCooperativeMatrixOpConstantNullTests`. It owns its own Level-3 page (`vktComputeCooperativeMatrixOpConstantNullTests.md`) and is therefore **not** the subject of this rewrite. The current page only mentions its delegation under `## Registration Hierarchy`.

## One Concrete Example

### Representative generated test leaf

Test name pattern (from mustpass):

```text
dEQP-VK.compute.pipeline.cooperative_matrix.khr_a.subgroupscope.length.float32_float32.buffer.rowmajor.linear
```

Behavior for this leaf:

1. The host picks one cooperative-matrix property matching `subgroup` scope, `float32` input and output, and the chosen size. It creates input/output buffers at bindings 0–3 sized for that property's M, N, K.
2. The shader compiles GLSL that declares `coopmat<float32_t, gl_ScopeSubgroup, M, N, gl_MatrixUseA> matA`, `matB`, `matC`, `matO`, with each matrix's `M`, `N`, and `K` declared as `const` and bound to spec constants.
3. The shader calls `coopMatLoad`/`coopMatStore` for A, B, and C with the row-major stride and the linear addressing path. Because `useType == UT_KHR_A`, the matrices are all constructed with `gl_MatrixUseA` (no separate use per matrix).
4. Because `testType == TT_LENGTH`, the shader does `matO = outputMatType(matO.length())`, producing a matrix whose every element equals the matrix's `length()`.
5. The host reads the output buffer and checks that every element equals `matO.length()`.

This is the simplest example. Other test types substitute the operation (matrix multiply, reduce, etc.), the layout (`linear` vs `tensorlayout`), the storage class (workgroup, physical_buffer, etc.), or the address method (linear, tensorlayout, blocksize, decode) while keeping the same overall structure.

### 64-bit indexing example

Test name pattern:

```text
dEQP-VK.compute.pipeline.cooperative_matrix.64b_indexing.coopmat_64b_rowmajor_largeoffset
```

Behavior:

1. The host creates a single 2 GiB storage buffer with `InputValue(ndx) = ndx ^ 0x82ce7f` written at every element.
2. The shader, compiled with SPIR-V 1.6, loads a `16 ×16` cooperative matrix at offset 5 GiB (past the 4 GiB boundary), complements every element, and stores it back.
3. The host walks every element: in-matrix elements must be `~InputValue(ndx)`; out-of-matrix elements must be `InputValue(ndx)` unchanged.

## End-to-End Test Flow

For the regular generated GLSL cases, the host does:

```text
1. [host] register test hierarchy and prune unsupported cases
   1.1 [host] enumerate UseType (nv, khr_a, khr_b, khr_c, khr_r)
   1.2 [host] enumerate scope (subgroupscope, workgroupscope)
   1.3 [host] enumerate test type (length, constant, composite, add, matrixmuladd, ...)
   1.4 [host] enumerate subgroup-size mode (none / _min / _max)
   1.5 [host] enumerate component type pair (float32_float32, uint8_uint32, ...)
   1.6 [host] enumerate storage class (buffer, workgroup, buffer_varptr, ..., physical_buffer)
   1.7 [host] enumerate colmajor (rowmajor, colmajor)
   1.8 [host] enumerate address method (linear, tensorlayout, blocksize, decode)
   1.9 [host] apply feature, property, and matrix-size gates

2. [host] add `convert`/`convert_sat` matrices (KHR use types except UT_KHR_C)
3. [host] add `multicomponent.load` and `multicomponent.save` matrices (KHR use types except UT_NV and UT_KHR_C)
4. [host] add `op_constant_null` subtree via delegated factory
5. [host] add non-VulkanSC `64b_indexing` subtree (six leaves)

6. [device] for each generated cooperative-matrix leaf
   6.A [host] checkSupport gates: Vulkan 1.1, cooperativeMatrix (KHR or NV),
       vulkanMemoryModel, variablePointers or bufferDeviceAddress if needed,
       shaderFloat16/bfloat16/float8 features, shader-object requirements,
       and VK_NV_cooperative_matrix2 feature subset
   6.B [host] gather VkCooperativeMatrixPropertiesKHR / FlexibleDimensionsProperties
       that match the chosen scope, types, and saturation
   6.C [host] pick one or more (M, N, K, workgroupSize) tuples; build input/output buffers
       sized by tuple, workgroup dims, and addressing method
   6.D [host] fill input buffers with deterministic pseudo-random data (or special
       floats for convert/sat), wrap inputs into a CoOpBufferVec host pointer view
   6.E [host] bind buffers to set 0 (binding 0..3 for SSBO use, binding 4 for
       physical_buffer); compile the generated GLSL or hand-written 64b GLSL into SPIR-V
   6.F [host] bind pipeline, descriptor sets, push constants, and dispatch
       (workgroupsX × workgroupsY × 1)
   6.G [device] shader loads A/B/C from buffers (or shared) into cooperative matrices,
       performs the chosen operation, stores matO to binding 3
   6.H [host] copy matO buffer back, run per-element reference comparison chosen
       by testType (epsilon for float, mask for integer, reduce reference for
       reduce ops, special bf16 threshold for bfloat16 outputs)

7. [host] report pass/fail based on whether any element mismatched the reference
```

For the `64b_indexing` subtree, the runtime flow is shorter (single dispatch with `1 × 1 × 1`, push-constant offset/stride/height, no per-element size matrix), but it still follows `host checkSupport → host prepare 2 GiB buffer → host dispatch → shader load/complement/store → host per-element comparison`.

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

| Artifact | Generated/loaded where | Role |
|---|---|---|
| Generated GLSL shader | `CooperativeMatrixTestCase::initPrograms()` [vktComputeCooperativeMatrixTests.cpp#L1183-L2230] | Produces the regular cooperative-matrix GLSL using template-style string concatenation. |
| Hand-written SPIR-V | `CooperativeMatrixTestCase::initProgramsSPIRV()` [vktComputeCooperativeMatrixTests.cpp#L2280-L2590+] | Used for some 8-bit-specific cases that hand-port the shader to SPIR-V assembly. |
| `64b_indexing` GLSL | `CoopMat64bTest::initPrograms()` [vktComputeCooperativeMatrixTests.cpp#L6240-L6283] | Generates the in-place complement GLSL for `64b_indexing`. |
| Specialization constants | Host pipeline setup | Local-size x/y, M, N, K, strides 0..3. |
| Push constants | `64b_indexing` and `TT_MATRIXMULADD_PUSH_CONSTANTS` | Provide large offsets, strides, or matrix strides when binding-based descriptors cannot express the value. |
| Pipeline | Host pipeline setup | Compute pipeline (`COMPUTE_PIPELINE_CONSTRUCTION_TYPE_PIPELINE`, or shader-object variants in non-VulkanSC builds). |
| `op_constant_null` subtree | `vktComputeCooperativeMatrixOpConstantNullTests.cpp` | Delegated registration only — separate Level-3 page. |

### Bound resources and memory objects

| Resource | Created by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|---|---|---|---|---|---|
| Buffer A | yes | binding 0 (SSBO use) or part of binding 4 (physical_buffer use) | read by device | no | Input matrix A. |
| Buffer B | yes | binding 1 (SSBO use) or part of binding 4 (physical_buffer use) | read by device | no | Input matrix B. |
| Buffer C | yes | binding 2 (SSBO use) or part of binding 4 (physical_buffer use) | read by device | no | Input accumulator C. |
| Output buffer | yes | binding 3 (SSBO use) or part of binding 4 (physical_buffer use) | written by device | yes | Shader writes matO; host compares every element. |
| Device-address buffer | yes (only when physical_buffer) | binding 4 | written by host before dispatch | no | Carries the four VkDeviceAddress values used by buffer-reference declarations in the shader. |
| `shared` matrices | no host object | none (workgroup-scope variants only) | read/write inside compute workgroup | no | When the storage class is `workgroup` or `workgroup_varptr`, A/B/C are pulled into shared memory at the start of the shader. |
| 2 GiB buffer (64b_indexing) | yes | binding 0 | read/write by device | yes | Single buffer that holds the matrix at the pushed offset. |
| Push constants (64b_indexing) | yes | stage = compute | read by device | no | `uint64_t offset`, `uint stride`, `uint height`. |
| Push constants (matrixmuladd_push) | yes | stage = compute | read by device | no | Stride pushed instead of baked into specialization constants. |
| Descriptor pool | yes | yes | n/a | n/a | Storage-buffer descriptors for bindings 0..3 (and 4 for physical_buffer). |

## What Is Checked

### Device-side pass condition

The host checks whether every output element matches the operation's reference value for that element. The reference rule depends on `testType`:

| Test type | Reference rule |
|---|---|
| `length` | every element equals the matrix's `length()`. |
| `constant` | every element equals `1.0` of the result type. |
| `add`, `sub`, `mul`, `div` | per-element operation on the loaded A/B values. |
| `matrixtimesscalar` | `(2 * A[i]) * 3` per element. |
| `func` / `func_const_in` | `-matA[i]` per element. |
| `matrixmuladd` and `_array` | `ref += A[i] * B[i]` for the K dimension, plus `C[i]`. For float output: `fabs(ref - Dij) <= epsilon` (with `epsilon = 1/2^17`); for smaller-than-32-bit output: bitmasked. For bfloat16: special threshold via `calcB16Threshold`. |
| `matrixmuladd_saturated` | saturated `ref + Cij`. |
| `matrixmuladd_wrapping` | `ref + Cij` truncated to the output bit width. |
| `matrixmuladd_stride0` | same as `matrixmuladd` but stride is zero on the load side. |
| `matrixmuladd_cross` | mixed-input-type accumulation variant. |
| `matrixmuladd_dequant` | decoded values from a 4bpp-encoded quantized buffer. |
| `convert` / `convert_sat` | round-to-nearest conversion between two component types; saturation clamps to the target's largest normal. |
| `convert_acc_to_a` / `_to_b`, `transpose_acc_to_b` | accumulator-to-A/B conversion or transpose, hard-coded under `UT_KHR_Result`. |
| `reduce_sum_*` / `reduce_min_*` | combined identity then `Combine()` across rows/cols/`2x2` blocks. |
| `per_element_op_*` | user-supplied element function applied during load or store. |
| `tensorlayout*` | matrix values written through `coopMatStoreTensorNV` with the tensor layout and view used to construct the host reference. |
| `clamp*` | per-tensor-coord clamp formula (constant/edge/repeat/mirror-repeat) used to construct the host reference. |
| `multicomponent.load` / `.save` | same as `add`/`sub` etc., but the source/dest type is `vec2` or `vec4`. |
| `64b_indexing` (six leaves) | in-matrix element equals `~input`; out-of-matrix element equals `input`. |

### Host-side checks

There is no fail buffer or copyback in this file. The host compares the output buffer against the per-element reference directly after the dispatch completes, looping over `(mX, mY, i, j)` for each cooperative matrix in the dispatch grid. If any element mismatches, the case logs the `(M, N, K, workgroupSize)` tuple and returns `QP_TEST_RESULT_FAIL`. If all matrix sizes for the chosen property pass, the case returns `QP_TEST_RESULT_PASS`.

## What Failure Means

A failure means one of:

- The implementation compiled the shader incorrectly (wrong lowering of a cooperative-matrix SPIR-V op).
- The implementation executed the shader but produced a wrong element value (for example, the wrong order of reductions, the wrong address math, the wrong component-type conversion).
- The implementation failed to report support for a feature combination that the CTS expects based on `VkCooperativeMatrixPropertiesKHR` / `VkCooperativeMatrixFlexibleDimensionsPropertiesNV`.

Possible bug areas include:

- Incorrect compiler lowering of `OpCooperativeMatrixLoad`, `OpCooperativeMatrixStore`, `OpCooperativeMatrixMulAdd`, `OpCooperativeMatrixTransposeNV`, `OpCooperativeMatrixReduceNV`, or `OpCooperativeMatrixPerElementOpNV`.
- Incorrect address math for `coopMatLoadTensorNV` (tensor layout, block size, decode) or for clamp variants.
- Wrong result for `OpCooperativeMatrixConvertNV` between mismatched component types or between signed and unsigned accumulators.
- Incorrect handling of `gl_MatrixUseA` / `gl_MatrixUseB` / `gl_MatrixUseAccumulator` distinctions.
- Incorrect handling of `subgroup` vs `workgroup` scope semantics.
- Wrong stride or row/column-major math in `coopMatLoad` / `coopMatStore`.
- Wrong reference-value computation for the host-side check (rare; the references are derived directly from the per-element input values and the chosen operation).

## Important Variations and Special Cases

### NV vs KHR use types

`UT_NV` uses the `fcoopmatNV<bits, scope, M, N>` template syntax and does not require a use type. `UT_KHR_*` uses `coopmat<T, scope, M, N, use>` and assigns the use type explicitly. The two branches cannot be mixed: the `UT_NV` matrix multiply skip rule excludes `UT_KHR_A`/`UT_KHR_B`, while the `UT_KHR_*` reduce skip rule excludes `UT_NV` (NV has no reduce op). `UT_KHR_C` cannot be used as a result operand; the matrix-C-only path is intentionally empty for `UT_KHR_C`.

### `matrixmuladd` M/N/K selection

`matrixmuladd` is the only test type whose dimensions actually depend on the subgroup size. The M/N/K tuple is chosen from `VkCooperativeMatrixPropertiesKHR` for the matching scope and types. For `UT_NV`, the property's `M × N × K` is the fixed shape. For `UT_KHR_*`, the property is fixed unless `cooperativeMatrixFlexibleDimensions` is supported, in which case the test enumerates `(M, N, K)` tuples that satisfy the property's granularity.

### Tensor layout / block / clamp branches

`tensorlayout1d` … `tensorlayout5d` and their `_clip` variants, plus `spacetodepth`, are produced only under `cooperativeMatrixFlexibleDimensions`. They use a 128×128 logical tensor with 4 workgroups in x and y, address elements via `coopMatLoadTensorNV` with `sliceTensorLayoutNV`, and check each tensor coordinate against the corresponding matrix coordinate in the host reference.

The `clamp*` variants use `setTensorLayoutClampValueNV` and a 6-element inset on each side; out-of-bounds load positions are clamped by the chosen mode (constant / edge / repeat / mirror-repeat), and out-of-bounds store positions are filled with `123` (or `17` for `clampconstant` load positions).

### `convert` / `multicomponent` branches

`convert` and `convert_sat` live in a separate matrix under `useType != UT_KHR_C`. They iterate over every input/output type combination from `allTypes`, where `allTypes` excludes 64-bit types (per source comment) and includes bfloat16 / E5M2 / E4M3 in non-VulkanSC builds. Saturation only pairs float-like input types with E5M2 / E4M3 output types. `multicomponent` lives under `useType != UT_NV && useType != UT_KHR_C`, and iterates over `vec2`/`vec4` source or destination types plus every component type in `allTypes`.

### 64-bit indexing

The `64b_indexing` subtree is intentionally simple: load the matrix at the pushed offset, complement every element, store it back, and verify every element. It uses handwritten GLSL (not the generator), the `64_BIT_INDEXING` pipeline-create flag, and the in-element complement rule. The host expects in-matrix elements to be `~input` and out-of-matrix elements to be `input` (they are skipped by the complement but still observable in the buffer).

## Source Mapping

| Topic | Source link | Why it matters |
|---|---|---|
| Package-level registration | [vktComputeTests.cpp#L48-L64](../../../modules/vulkan/compute/vktComputeTests.cpp#L48-L64), [vktComputeTests.cpp#L68-L85](../../../modules/vulkan/compute/vktComputeTests.cpp#L68-L85) | Wires `createCooperativeMatrixTests` into the `compute.pipeline` subtree, gated to non-VulkanSC builds. |
| Factory declaration | [vktComputeCooperativeMatrixTests.hpp#L37-L38](../../../modules/vulkan/compute/vktComputeCooperativeMatrixTests.hpp#L37-L38) | Declares `createCooperativeMatrixTests`. |
| Root factory body | [vktComputeCooperativeMatrixTests.cpp#L6475-L6507](../../../modules/vulkan/compute/vktComputeCooperativeMatrixTests.cpp#L6475-L6507) | Adds the five use-type children, calls the delegated `op_constant_null` factory, and adds `64b_indexing` for non-VulkanSC builds. |
| Internal matrix factory | [vktComputeCooperativeMatrixTests.cpp#L5522-L6185](../../../modules/vulkan/compute/vktComputeCooperativeMatrixTests.cpp#L5522-L6185) | Builds the nested scope/test-type/component/storage/layout/address matrices and adds `convert`/`multicomponent` branches. |
| Use-type string mapping | [vktComputeCooperativeMatrixTests.cpp#L5503-L5520](../../../modules/vulkan/compute/vktComputeCooperativeMatrixTests.cpp#L5503-L5520) | Maps `UT_NV` → `nv`, `UT_KHR_A` → `khr_a`, etc. |
| Support gating | [vktComputeCooperativeMatrixTests.cpp#L739-L1027](../../../modules/vulkan/compute/vktComputeCooperativeMatrixTests.cpp#L739-L1027) | API version, cooperative-matrix features, scope/use/type/feature subset, bfloat16 / float8 features. |
| Generated GLSL | [vktComputeCooperativeMatrixTests.cpp#L1183-L2230](../../../modules/vulkan/compute/vktComputeCooperativeMatrixTests.cpp#L1183-L2230) | Per-case shader built by string concatenation. |
| Hand-written SPIR-V | [vktComputeCooperativeMatrixTests.cpp#L2280-L2590](../../../modules/vulkan/compute/vktComputeCooperativeMatrixTests.cpp#L2280-L2590) | Used for cases that need assembly-level control. |
| Runtime buffer setup | [vktComputeCooperativeMatrixTests.cpp#L3210-L3426](../../../modules/vulkan/compute/vktComputeCooperativeMatrixTests.cpp#L3210-L3426) | Builds input/output buffers, device-address buffer for physical_buffer, descriptor sets. |
| Runtime dispatch | [vktComputeCooperativeMatrixTests.cpp#L5474-L5501](../../../modules/vulkan/compute/vktComputeCooperativeMatrixTests.cpp#L5474-L5501) | Records `QP_TEST_RESULT_FAIL` on the first mismatch and returns the final result. |
| `64b_indexing` test case | [vktComputeCooperativeMatrixTests.cpp#L6187-L6467](../../../modules/vulkan/compute/vktComputeCooperativeMatrixTests.cpp#L6187-L6467) | Defines `CoopMat64bTest` and `CoopMat64bTestInstance`. |
| `op_constant_null` delegation | [vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1847-L1866](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1847-L1866) | Delegated factory, separate Level-3 page. |

## Questions / Risk Points for User Audit

- [x] The primary behavioral axis is the **use type** (`nv`, `khr_a`, `khr_b`, `khr_c`, `khr_r`), because each use type changes the matrix declarations in the shader, the matrix-operation skip rules, and which feature gates apply.
- [x] The 64-bit indexing subtree is structurally separate from the generated matrix; it deserves its own subsection but not its own walkthrough because its behavior is intentionally simple.
- [x] The `op_constant_null` subtree is delegated; this page must not duplicate its content, only mention the delegation.
- [ ] Audit whether the per-operation reference rule should be inlined into a single combined table or kept under each behavior-parameter subsection. The combined table is more compact; the per-operation narrative is more readable.
- [ ] Audit mustpass line anchors before publishing; the `vk-default/compute.txt` file holds concrete leaf names that can be cited as evidence.
- [ ] `UT_KHR_Result` (`khr_r`) hosts the only accumulator-conversion and transpose tests; this is non-obvious and should be called out clearly in the page.

## Conversion Notes for Final Wiki Rewrite

- Keep the use-type (`nv`, `khr_a`, `khr_b`, `khr_c`, `khr_r`) grouping as the primary behavioral axis in `## Behavior Parameters`.
- Distill the background into a compact prerequisite list: cooperative matrix concept, scope + use type interaction, address method, storage class, component-type rules, test types, and the role of `op_constant_null`/`64b_indexing` as separate subtrees.
- Treat the regular generated matrix walkthrough as the single representative shader walkthrough. The `64b_indexing` subtree does not need its own walkthrough because it uses handwritten GLSL that already has only one simple structure.
- Keep `64b_indexing` and `op_constant_null` mentioned under `## Registration Hierarchy` and `## Behavior Parameters`, but route their deeper explanation to their own subtrees.
- Move detailed pruning rules and feature gates into `## Case Pruning` rather than the main narrative.
- Move detailed host-side reference formulas into `## Runtime Execution and Result Checking` and the per-test-type reference table into `## Failure Meaning`.
- Do not copy the brief's beginner-focused prose verbatim into the final page; convert it to the Level-3 wiki style.

## Conversion Notes for the Vulkan Spec Chapter

The `external/vulkan-docs/src/chapters/` tree is not present in this checkout. Cooperative matrix semantics in this rewrite are grounded in CTS source code, registration evidence, and mustpass examples. Flag this limitation explicitly in the final page's `## Conversion Notes` if relevant.