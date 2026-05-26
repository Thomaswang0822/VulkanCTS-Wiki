# vktShaderBFloat16Tests.cpp

## Overview

[`vktShaderBFloat16Tests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBFloat16Tests.cpp#L1) is the
registration and shared-helper file for GLSL `bfloat16` tests. The GLSL category adds this group under `glsl` only for
non-Vulkan SC builds in [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1253-L1259). The file defines
shared `bf16` helper type-name and extension-name mappings, then constructs the registered `bfloat16` group and delegates
its direct children to dot-product, specialization-constant, and compute-operation implementation files in
[`createBFloat16Tests()`](../../../modules/vulkan/shaderexecutor/vktShaderBFloat16Tests.cpp#L200-L211).

## Role

Registration / aggregation file with shared helper definitions. The file itself does not implement individual
`TestInstance` execution logic; it registers the root `bfloat16` group and calls the three factory functions that add the
`dot`, `constant`, and `various` child groups.

## Source Code

- Primary source: [`vktShaderBFloat16Tests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBFloat16Tests.cpp#L1-L215)
- Root header and shared aligned BF16 vector helpers: [`vktShaderBFloat16Tests.hpp`](../../../modules/vulkan/shaderexecutor/vktShaderBFloat16Tests.hpp#L74-L177)
- Dot-product implementation: [`vktShaderBFloat16DotTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBFloat16DotTests.cpp#L1-L358)
- Specialization-constant implementation: [`vktShaderBFloat16ConstantTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBFloat16ConstantTests.cpp#L1-L1175)
- Composite/access-chain/function-call/swizzle implementation: [`vktShaderBFloat16ComboTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBFloat16ComboTests.cpp#L1-L890)
- GLSL category registration site: [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1253-L1259)

## Registration Hierarchy

```text
glsl.bfloat16
├── dot
├── constant
└── various
```

## Test Families

### dot — BFloat16 vector dot-product compute cases

The `dot` group is created by
[`createBFloat16DotTests()`](../../../modules/vulkan/shaderexecutor/vktShaderBFloat16DotTests.cpp#L341-L357) and adds
three direct cases named `vec2`, `vec3`, and `vec4` from the `cases[]` table at
[`vktShaderBFloat16DotTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBFloat16DotTests.cpp#L343-L347). Each
case uses `GL_EXT_bfloat16` through the shared extension mapping in
[`vktShaderBFloat16Tests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBFloat16Tests.cpp#L37-L46) and specializes
the shader with BF16 vector type names from
[`vktShaderBFloat16Tests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBFloat16Tests.cpp#L48-L67).

Execution is compute-only: the instance creates storage buffers for two BF16-vector inputs and one scalar BF16 output,
binds them to a compute pipeline, pushes the selected vector width, and dispatches one workgroup per generated input
record at [`BFloat16OpDotInstance::iterate()`](../../../modules/vulkan/shaderexecutor/vktShaderBFloat16DotTests.cpp#L182-L251).
The input count is pseudo-random but bounded by the modulo-64 expression at
[`vktShaderBFloat16DotTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBFloat16DotTests.cpp#L189-L194), and
each generated input element can include finite values, NaNs, or infinities at
[`generateInputData()`](../../../modules/vulkan/shaderexecutor/vktShaderBFloat16DotTests.cpp#L264-L289).

### constant — Specialization constants for BF16 and FP8 scalar/vector shader types

The `constant` group is created by
[`createBFloat16ConstantTests()`](../../../modules/vulkan/shaderexecutor/vktShaderBFloat16ConstantTests.cpp#L1150-L1175).
It registers nine cases: `computebf16`, `vertexbf16`, `fragmentbf16`, `computefe5m2`, `vertexfe5m2`, `fragmentfe5m2`,
`computefe4m3`, `vertexfe4m3`, and `fragmentfe4m3`, all listed in the local factory table at
[`vktShaderBFloat16ConstantTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBFloat16ConstantTests.cpp#L1153-L1163).

The compute variants embed specialization constants in local-size IDs and scalar constants, then write selected values
into a storage buffer at
[`BFloat16ConstantCaseT<VK_SHADER_STAGE_COMPUTE_BIT>::initPrograms()`](../../../modules/vulkan/shaderexecutor/vktShaderBFloat16ConstantTests.cpp#L409-L456).
The vertex and fragment variants use constant IDs `0` through `13` in graphics-stage shaders, with the vertex path
writing a storage buffer and position data at
[`vktShaderBFloat16ConstantTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBFloat16ConstantTests.cpp#L458-L517) and
the fragment path writing storage-buffer data from the fragment shader at
[`vktShaderBFloat16ConstantTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBFloat16ConstantTests.cpp#L519-L560).
The shared type-name mapping covers BF16, FloatE5M2, and FloatE4M3 extension/type spellings at
[`vktShaderBFloat16Tests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBFloat16Tests.cpp#L37-L67) and
[`vktShaderBFloat16Tests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBFloat16Tests.cpp#L146-L196).

### various — Composite, access-chain, function-call, and swizzle compute cases

The `various` group is created by
[`createBFloat16ComboTests()`](../../../modules/vulkan/shaderexecutor/vktShaderBFloat16ComboTests.cpp#L878-L890). It adds
four direct cases named `composites`, `access_chains`, `function_call`, and `swizzling` at
[`vktShaderBFloat16ComboTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBFloat16ComboTests.cpp#L883-L887).

All four cases are compute tests using storage buffers and one 32-bit push constant variant selector in the shared
`BFloat16ComboTestInstance::iterate()` path at
[`vktShaderBFloat16ComboTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBFloat16ComboTests.cpp#L801-L873). The
`composites` shader copies BF16 scalar/vector fields between two structure instances at
[`vktShaderBFloat16ComboTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBFloat16ComboTests.cpp#L208-L237). The
`access_chains` shader copies nested structure and array members through selected access chains at
[`vktShaderBFloat16ComboTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBFloat16ComboTests.cpp#L434-L485). The
`function_call` shader tests BF16 scalar and vector parameters returned directly and via `out` parameters, with two
registered runtime variants (`ret_in` and `ret_ref`) in
[`vktShaderBFloat16ComboTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBFloat16ComboTests.cpp#L575-L707). The
`swizzling` case uses BF16 scalar/vector swizzle forms and validates permutations generated by `next_permutation()` at
[`BFloat16ComboInstance<Swizzling>::verifyResult()`](../../../modules/vulkan/shaderexecutor/vktShaderBFloat16ComboTests.cpp#L407-L431).

## Parameter Dimensions

| Dimension | Observed values / evidence |
|---|---|
| Registered root and direct children | `createBFloat16Tests()` constructs `bfloat16` and delegates `dot`, `constant`, and `various` child creation at [`vktShaderBFloat16Tests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBFloat16Tests.cpp#L204-L211). |
| Build scope | The GLSL package registers `bfloat16` only inside `#ifndef CTS_USES_VULKANSC` at [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1253-L1259). |
| Dot vector widths | `vec2`, `vec3`, and `vec4` from the dot `cases[]` table at [`vktShaderBFloat16DotTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBFloat16DotTests.cpp#L343-L347). |
| Dot input population | The dot instance chooses a pseudo-random count modulo 64, creates BF16 vector input/output buffers, and dispatches `ioCount` workgroups at [`vktShaderBFloat16DotTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBFloat16DotTests.cpp#L189-L251). |
| Constant float formats | BF16, FloatE5M2, and FloatE4M3 are represented by the nine factory-table entries at [`vktShaderBFloat16ConstantTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBFloat16ConstantTests.cpp#L1153-L1163). |
| Constant shader stages | Compute, vertex, and fragment are encoded by the `BFloat16ConstantCaseT` specializations and the nine case names at [`vktShaderBFloat16ConstantTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBFloat16ConstantTests.cpp#L376-L405) and [`vktShaderBFloat16ConstantTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBFloat16ConstantTests.cpp#L1153-L1163). |
| Constant IDs | Compute uses local-size specialization IDs `0`, `2`, and `4` plus constants `1`, `3`, `5` through `11`; vertex and fragment use constants `0` through `13` at [`vktShaderBFloat16ConstantTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBFloat16ConstantTests.cpp#L413-L447), [`vktShaderBFloat16ConstantTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBFloat16ConstantTests.cpp#L462-L499), and [`vktShaderBFloat16ConstantTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBFloat16ConstantTests.cpp#L523-L560). |
| Various operation families | `composites`, `access_chains`, `function_call`, and `swizzling` are added under `various` at [`vktShaderBFloat16ComboTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBFloat16ComboTests.cpp#L883-L887). |
| Function-call runtime variants | `function_call` dispatches two push-constant variants, `ret_in` and `ret_ref`, from [`getVariants()`](../../../modules/vulkan/shaderexecutor/vktShaderBFloat16ComboTests.cpp#L701-L707). |
| GLSL extension/type spelling | BF16 maps to `GL_EXT_bfloat16`, `bfloat16_t`, and `bf16vec2`/`bf16vec3`/`bf16vec4`; FloatE5M2 and FloatE4M3 map to `GL_EXT_float_e5m2`/`GL_EXT_float_e4m3` and `fe5m2*`/`fe4m3*` type names at [`vktShaderBFloat16Tests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBFloat16Tests.cpp#L37-L67) and [`vktShaderBFloat16Tests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBFloat16Tests.cpp#L146-L196). |

## Support / Feature Requirements

| Requirement | Evidence |
|---|---|
| 16-bit storage buffers | Dot, constant, and various cases require `storageBuffer16BitAccess` before using 16-bit-like scalar/vector types in storage buffers at [`vktShaderBFloat16DotTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBFloat16DotTests.cpp#L83-L88), [`vktShaderBFloat16ConstantTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBFloat16ConstantTests.cpp#L135-L140), and [`vktShaderBFloat16ComboTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBFloat16ComboTests.cpp#L72-L77). |
| BF16 type support | Dot and constant BF16 paths require `shaderBFloat16Type`; the dot path also requires `shaderBFloat16DotProduct`, and the combo path requires `shaderBFloat16Type` for all `various` cases at [`vktShaderBFloat16DotTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBFloat16DotTests.cpp#L90-L96), [`vktShaderBFloat16ConstantTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBFloat16ConstantTests.cpp#L142-L148), and [`vktShaderBFloat16ComboTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBFloat16ComboTests.cpp#L79-L82). |
| FP8 support for constant cases | FloatE5M2 and FloatE4M3 constant cases require `shaderFloat8` at [`vktShaderBFloat16ConstantTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBFloat16ConstantTests.cpp#L149-L155). |
| Vulkan SC exclusion | Registration under the GLSL package excludes this root when `CTS_USES_VULKANSC` is defined at [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1256-L1259). |

## Verification Methods

- Dot-product cases invalidate the output buffer, recompute each expected dot product on the CPU over the selected vector
  width, require NaN output when either input vector has a NaN in the active components, and fail if any output differs
  from the recomputed value at
  [`BFloat16OpDotInstance::verifyResults()`](../../../modules/vulkan/shaderexecutor/vktShaderBFloat16DotTests.cpp#L292-L337).
- Compute specialization-constant cases build a CPU reference set from the same specialization values, including the
  local-size constants, and compare the first three output `vec4` records component-by-component after invalidating the
  buffer at
  [`BFloat16ComputeInstance::verifyResult()`](../../../modules/vulkan/shaderexecutor/vktShaderBFloat16ConstantTests.cpp#L606-L680).
- Vertex specialization-constant cases compare storage-buffer values with prepared vertices and sample the barycentric
  point of each expected triangle for white pixels at
  [`BFloat16VertexInstance::verifyResult()`](../../../modules/vulkan/shaderexecutor/vktShaderBFloat16ConstantTests.cpp#L947-L996).
- Fragment specialization-constant cases compare storage-buffer values with prepared vertices and require barycentric
  triangle samples to contain the expected per-triangle color vector at
  [`BFloat16FragmentInstance::verifyResult()`](../../../modules/vulkan/shaderexecutor/vktShaderBFloat16ConstantTests.cpp#L1090-L1140).
- Various-operation cases use operation-specific host comparisons after compute execution: composites compare swapped
  structures, access chains compare selected nested members, function calls compare reordered scalar/vector return values,
  and swizzling compares generated output permutations at
  [`vktShaderBFloat16ComboTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBFloat16ComboTests.cpp#L284-L290),
  [`vktShaderBFloat16ComboTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBFloat16ComboTests.cpp#L550-L572),
  [`vktShaderBFloat16ComboTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBFloat16ComboTests.cpp#L710-L794), and
  [`vktShaderBFloat16ComboTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBFloat16ComboTests.cpp#L407-L431).
- The shared combo execution path clears the output buffer, writes generated input data, dispatches every variant returned
  by `getVariants()`, reads back the output buffer, and converts a failed operation-specific verification into
  `tcu::TestStatus::fail` at
  [`BFloat16ComboTestInstance::iterate()`](../../../modules/vulkan/shaderexecutor/vktShaderBFloat16ComboTests.cpp#L801-L873).

## Test Principles

- The Level-3 root is a narrow non-Vulkan-SC GLSL branch for shader bfloat16 functionality, not a whole-category GLSL
  dispatcher; the actual root registration is the `bfloat16` group returned by
  [`createBFloat16Tests()`](../../../modules/vulkan/shaderexecutor/vktShaderBFloat16Tests.cpp#L204-L211) and attached under
  `glsl` in [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1253-L1259).
- The aggregator keeps the parseable hierarchy shallow (`dot`, `constant`, `various`) while implementation files expand
  generated cases and operation-specific validation, as shown by the three external factory declarations and calls in
  [`vktShaderBFloat16Tests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBFloat16Tests.cpp#L200-L209).
- The tests pair shader execution with host-side reference checking rather than relying only on successful compilation or
  dispatch: dot uses CPU dot recomputation, constant cases compare specialization-derived storage/image observations, and
  combo cases compare operation-specific output data.
- Shared type-name and extension-name helpers centralize the GLSL spellings for BF16 and the FP8 formats used by the
  constant cases at [`vktShaderBFloat16Tests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBFloat16Tests.cpp#L37-L67)
  and [`vktShaderBFloat16Tests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBFloat16Tests.cpp#L146-L196).

## Notes / Uncertainties

- The `constant` family includes BF16 and FP8 cases; the inspected registration table does not include Float16 constant
  cases under this `bfloat16` root at
  [`vktShaderBFloat16ConstantTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBFloat16ConstantTests.cpp#L1153-L1163).
- The aggregator file itself supplies shared BF16/FP8 naming helpers and registration only; execution, support checks, and
  verification live in the three inspected implementation files listed in the Source Code section.
