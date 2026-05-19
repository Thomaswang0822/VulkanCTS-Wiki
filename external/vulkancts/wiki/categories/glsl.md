# GLSL

## Overview

The `glsl` category tests GLSL shader language features: operators, control flow, built-in functions, precision, texture functions, and shader-stage-specific behavior. It is one of the largest categories in the Vulkan CTS, covering the full range of GLSL ES 3.10 and GLSL 4.40 functionality that Vulkan shaders rely on.

## Registration Architecture

The `glsl` category has a **unique registration architecture** that differs from every other Vulkan CTS category. Most categories own a dedicated source directory under `modules/vulkan/{category}/` with a root registration file. The `glsl` category does **not** have a `modules/vulkan/glsl/` directory. Instead, its registration entry point lives in the global test package file, and its implementation files are spread across four separate directories.

### How It Works

1. **Root registration** — [vktTestPackage.cpp#L1353](../../modules/vulkan/vktTestPackage.cpp#L1353) calls `addRootChild("glsl", ..., createGlslTests)`, which creates the top-level `"glsl"` group.

2. **Aggregator function** — `createGlslTests()` at [vktTestPackage.cpp#L1215-L1288](../../modules/vulkan/vktTestPackage.cpp#L1215-L1288) populates the `glsl` group by calling `glslTests->addChild(...)` for each sub-group factory. This is the **only** place where these files are attached to the `glsl` tree. The same source files are not registered under any other category.

3. **Four source directories** — The sub-group factories come from four directories:

   | Directory | Namespace | Test Framework | Groups Registered |
   |-----------|-----------|----------------|-------------------|
   | `modules/vulkan/shaderrender/` | `sr::` | ShaderRenderCase | derivate, discard, demote, indexing, invariance, precise, limits, loops, matrix, operator, return, struct, switch, texture_functions, texture_gather, builtin_var |
   | `modules/vulkan/shaderexecutor/` | `shaderexecutor::` | ShaderExecutor | builtin, opaque_type_indexing, atomic_operations, shader_clock, helper_invocations, bfloat16, shader_expect_assume |
   | `modules/vulkan/amber/` | `cts_amber::` | Amber | combined_operations, crash_test, logical_copy |
   | (via `vktShaderLibrary.cpp`) | (global) | ShaderLibrary / .test files | arrays, conditionals, constant_expressions, constants, conversions, functions, linkage, scoping, swizzles, 440 |

4. **Registration chain** — A test ends up under `dEQP-VK.glsl.*` not because of its filesystem location, but because its factory function was called via `glslTests->addChild()`. For example:
   - `vktTestPackage.cpp` creates `"glsl"` group
   - `createGlslTests()` calls `glslTests->addChild(sr::createDerivateTests(...))`
   - `createDerivateTests()` returns a `ShaderDerivateTests` group constructed with name `"derivate"`
   - Result: `dEQP-VK.glsl.derivate`

### Why This Matters

When navigating the source code for `glsl` tests, you cannot find them by looking for a `modules/vulkan/glsl/` directory. Instead, you must trace from the `createGlslTests()` function in `vktTestPackage.cpp` to identify which files contribute to this category. The four directories (`shaderrender/`, `shaderexecutor/`, `amber/`, and the ShaderLibrary infrastructure) are shared with other categories in principle, but in practice each factory function is only called once under `glsl`.

## Registration Entry Point

[vktTestPackage.cpp#L1215-L1288](../../modules/vulkan/vktTestPackage.cpp#L1215-L1288) — `createGlslTests()`

## Subgroup Structure

```text
glsl
├── arrays                          (ShaderLibrary, es310/arrays.test)
├── conditionals                    (ShaderLibrary, es310/conditionals.test)
├── constant_expressions            (ShaderLibrary, es310/constant_expressions.test)
├── constants                       (ShaderLibrary, es310/constants.test)
├── conversions                     (ShaderLibrary, es310/conversions.test)
├── functions                       (ShaderLibrary, es310/functions.test)
├── linkage                         (ShaderLibrary, es310/linkage.test)
├── scoping                         (ShaderLibrary, es310/scoping.test)
├── swizzles                        (ShaderLibrary, es310/swizzles.test)
├── 440                             (intermediate group)
│   └── linkage                     (ShaderLibrary, 440/linkage.test)
├── derivate                        (shaderrender)
├── discard                         (shaderrender)
├── demote                          (shaderrender, non-VulkanSC only)
├── indexing                        (shaderrender)
├── invariance                      (shaderrender)
├── precise                         (shaderrender)
├── limits                          (shaderrender)
├── loops                           (shaderrender)
├── matrix                          (shaderrender)
├── operator                        (shaderrender)
├── return                          (shaderrender)
├── struct                          (shaderrender)
├── switch                          (shaderrender)
├── texture_functions               (shaderrender)
├── texture_gather                  (shaderrender)
├── builtin_var                     (shaderrender)
├── builtin                         (shaderexecutor)
├── opaque_type_indexing            (shaderexecutor)
├── atomic_operations               (shaderexecutor)
├── shader_clock                    (shaderexecutor)
├── helper_invocations              (shaderexecutor)
├── bfloat16                        (shaderexecutor, non-VulkanSC only)
├── shader_expect_assume            (shaderexecutor, non-VulkanSC only)
├── combined_operations             (amber, non-VulkanSC only)
├── crash_test                      (amber, non-VulkanSC only)
└── logical_copy                    (amber, non-VulkanSC only)
```

## File Inventory

### ShaderLibrary Infrastructure

| File | Role | Level-3 Doc |
|------|------|-------------|
| [vktShaderLibrary.cpp](../../modules/vulkan/vktShaderLibrary.cpp) | Shared infrastructure — parses `.test` files and generates test groups | [vktShaderLibrary.cpp.md](../testfiles/glsl/vktShaderLibrary.cpp.md) |
| [vktShaderLibrary.hpp](../../modules/vulkan/vktShaderLibrary.hpp) | Header for ShaderLibraryGroup | — |
| `data/vulkan/glsl/es310/*.test` (9 files) | Declarative ES 3.10 test definitions | — |
| `data/vulkan/glsl/440/*.test` (1 file) | Declarative GLSL 4.40 test definitions | — |

### ShaderRender Files

| File | Group(s) | Level-3 Doc |
|------|----------|-------------|
| [vktShaderRenderDerivateTests.cpp](../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp) | derivate | [vktShaderRenderDerivateTests.cpp.md](../testfiles/glsl/vktShaderRenderDerivateTests.cpp.md) |
| [vktShaderRenderDiscardTests.cpp](../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp) | discard, demote | [vktShaderRenderDiscardTests.cpp.md](../testfiles/glsl/vktShaderRenderDiscardTests.cpp.md) |
| [vktShaderRenderIndexingTests.cpp](../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp) | indexing | [vktShaderRenderIndexingTests.cpp.md](../testfiles/glsl/vktShaderRenderIndexingTests.cpp.md) |
| [vktShaderRenderInvarianceTests.cpp](../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp) | invariance, precise | [vktShaderRenderInvarianceTests.cpp.md](../testfiles/glsl/vktShaderRenderInvarianceTests.cpp.md) |
| [vktShaderRenderLimitTests.cpp](../../modules/vulkan/shaderrender/vktShaderRenderLimitTests.cpp) | limits | [vktShaderRenderLimitTests.cpp.md](../testfiles/glsl/vktShaderRenderLimitTests.cpp.md) |
| [vktShaderRenderLoopTests.cpp](../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp) | loops | [vktShaderRenderLoopTests.cpp.md](../testfiles/glsl/vktShaderRenderLoopTests.cpp.md) |
| [vktShaderRenderMatrixTests.cpp](../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp) | matrix | [vktShaderRenderMatrixTests.cpp.md](../testfiles/glsl/vktShaderRenderMatrixTests.cpp.md) |
| [vktShaderRenderOperatorTests.cpp](../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp) | operator | [vktShaderRenderOperatorTests.cpp.md](../testfiles/glsl/vktShaderRenderOperatorTests.cpp.md) |
| [vktShaderRenderReturnTests.cpp](../../modules/vulkan/shaderrender/vktShaderRenderReturnTests.cpp) | return | [vktShaderRenderReturnTests.cpp.md](../testfiles/glsl/vktShaderRenderReturnTests.cpp.md) |
| [vktShaderRenderStructTests.cpp](../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp) | struct | [vktShaderRenderStructTests.cpp.md](../testfiles/glsl/vktShaderRenderStructTests.cpp.md) |
| [vktShaderRenderSwitchTests.cpp](../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp) | switch | [vktShaderRenderSwitchTests.cpp.md](../testfiles/glsl/vktShaderRenderSwitchTests.cpp.md) |
| [vktShaderRenderTextureFunctionTests.cpp](../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp) | texture_functions | [vktShaderRenderTextureFunctionTests.cpp.md](../testfiles/glsl/vktShaderRenderTextureFunctionTests.cpp.md) |
| [vktShaderRenderTextureGatherTests.cpp](../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp) | texture_gather | [vktShaderRenderTextureGatherTests.cpp.md](../testfiles/glsl/vktShaderRenderTextureGatherTests.cpp.md) |
| [vktShaderRenderBuiltinVarTests.cpp](../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp) | builtin_var | [vktShaderRenderBuiltinVarTests.cpp.md](../testfiles/glsl/vktShaderRenderBuiltinVarTests.cpp.md) |

### ShaderExecutor Files

| File | Group | Level-3 Doc |
|------|-------|-------------|
| [vktShaderBuiltinTests.cpp](../../modules/vulkan/shaderexecutor/vktShaderBuiltinTests.cpp) | builtin | [vktShaderBuiltinTests.cpp.md](../testfiles/glsl/vktShaderBuiltinTests.cpp.md) |
| [vktOpaqueTypeIndexingTests.cpp](../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp) | opaque_type_indexing | [vktOpaqueTypeIndexingTests.cpp.md](../testfiles/glsl/vktOpaqueTypeIndexingTests.cpp.md) |
| [vktAtomicOperationTests.cpp](../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp) | atomic_operations | [vktAtomicOperationTests.cpp.md](../testfiles/glsl/vktAtomicOperationTests.cpp.md) |
| [vktShaderClockTests.cpp](../../modules/vulkan/shaderexecutor/vktShaderClockTests.cpp) | shader_clock | [vktShaderClockTests.cpp.md](../testfiles/glsl/vktShaderClockTests.cpp.md) |
| [vktShaderHelperInvocationsTests.cpp](../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp) | helper_invocations | [vktShaderHelperInvocationsTests.cpp.md](../testfiles/glsl/vktShaderHelperInvocationsTests.cpp.md) |
| [vktShaderBFloat16Tests.cpp](../../modules/vulkan/shaderexecutor/vktShaderBFloat16Tests.cpp) | bfloat16 | [vktShaderBFloat16Tests.cpp.md](../testfiles/glsl/vktShaderBFloat16Tests.cpp.md) |
| [vktShaderExpectAssumeTests.cpp](../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp) | shader_expect_assume | [vktShaderExpectAssumeTests.cpp.md](../testfiles/glsl/vktShaderExpectAssumeTests.cpp.md) |

### Amber Files

| File | Group(s) | Level-3 Doc |
|------|----------|-------------|
| [vktAmberGlslTests.cpp](../../modules/vulkan/amber/vktAmberGlslTests.cpp) | combined_operations, crash_test, logical_copy | [vktAmberGlslTests.cpp.md](../testfiles/glsl/vktAmberGlslTests.cpp.md) |

## Cross-File Recurring Test Families

### ShaderRenderCase Family

The `shaderrender/` files share a common `ShaderRenderCase` base class that renders a fullscreen quad with a test-specific shader and compares the output against a reference computed by a `ShaderEvaluator` callback. This pattern is used by: derivate, discard, demote, indexing, invariance, precise, limits, loops, matrix, operator, return, struct, switch, texture_functions, texture_gather, builtin_var.

### ShaderExecutor Family

The `shaderexecutor/` files use a compute-pipeline or graphics-pipeline executor that runs a shader and reads back output buffers for comparison. This pattern is used by: builtin, opaque_type_indexing, atomic_operations, shader_clock, helper_invocations, bfloat16, shader_expect_assume.

### ShaderLibrary Family

The `vktShaderLibrary.cpp` infrastructure parses declarative `.test` files and generates `ShaderCase` instances that render with the specified shader sources and compare against expected output values. The `both` keyword in `.test` files automatically generates `_vertex` and `_fragment` suffixed test cases.

### Amber Family

The `vktAmberGlslTests.cpp` file creates Amber test cases from `.amber` script files, each defining its own verification logic.

## Cross-File Recurring Parameter Dimensions

| Dimension | Values | Used By |
|-----------|--------|---------|
| Shader stage | vertex, fragment | derivate, discard, demote, indexing, invariance, precise, loops, matrix, operator, return, struct, switch, texture_functions, texture_gather, builtin_var, opaque_type_indexing, atomic_operations, shader_clock, bfloat16, shader_expect_assume |
| Shader stage (extended) | geometry, tess_ctrl, tess_eval, compute, task, mesh | opaque_type_indexing, atomic_operations, shader_clock, texture_functions, texture_gather, shader_expect_assume |
| Precision | mediump, highp | derivate, loops, matrix, operator, invariance, precise |
| Data type | float, vec2, vec3, vec4, int, ivec2-4, uint, uvec2-4, bool, bvec2-4 | derivate, indexing, loops, matrix, operator, struct, atomic_operations |
| Matrix type | mat2, mat2x3, mat2x4, mat3x2, mat3, mat3x4, mat4x2, mat4x3, mat4 | matrix, indexing |
| Control flow type | static, uniform, dynamic | loops, switch, indexing, return |
| Texture type | 1D, 2D, 3D, Cube, 2DArray, 1DArray, CubeArray | texture_functions, texture_gather, derivate |

## Cross-File Recurring Support Requirements

| Requirement | Groups Affected |
|-------------|-----------------|
| `VK_KHR_shader_subgroup_uniform_control_flow` | derivate (subgroup variants) |
| `VK_EXT_shader_demote_to_helper_invocation` | demote, derivate (demote-to-helper variants) |
| `VK_KHR_shader_clock` | shader_clock |
| `VK_KHR_shader_expect_assume` | shader_expect_assume |
| `VK_KHR_shader_bfloat16` / `shaderBFloat16Type` | bfloat16 |
| `VK_KHR_shader_atomic_int64` | atomic_operations (int64/uint64) |
| `VK_EXT_shader_atomic_float` | atomic_operations (float32/float64) |
| `VK_EXT_shader_atomic_float2` | atomic_operations (float16/float32 minmax/float64 minmax) |
| `VK_NV_shader_atomic_float16_vector` | atomic_operations (f16vec2/f16vec4) |
| `VK_KHR_buffer_device_address` | atomic_operations (reference memory), helper_invocations (load_from_address) |
| `VK_KHR_storage_buffer_storage_class` | opaque_type_indexing (ssbo_storage_buffer_decoration) |
| `VK_KHR_16bit_storage` | shader_expect_assume (Int16), builtin (precision_fp16) |
| `VK_KHR_shader_float16_int8` | shader_expect_assume (Int8), builtin (precision_fp16) |
| `VK_KHR_8bit_storage` | shader_expect_assume (Int8) |
| `shaderFloat64` | builtin (precision_double) |
| `Features.tessellationShader` | crash_test (divbyzero_tesc/tese) |
| `Features.geometryShader` | crash_test (divbyzero_geom) |
| Sparse residency support | texture_functions, texture_gather (sparse variants) |
| Sample rate shading | builtin_var (MSAA tests) |
| `depthClamp` device feature | builtin_var (FragDepth depth clamp tests) |

## Cross-File Recurring Verification Methods

| Method | Description | Used By |
|--------|-------------|---------|
| ShaderEvaluator reference comparison | Render with test shader, compare against reference computed by evaluator callback | Most shaderrender files |
| Interval-based comparison | Compute analytical bounds using `tcu::Interval`, verify output falls within bounds | derivate |
| Dual-shader rendering | Render same scene with two vertex shaders, verify pixel-identical output | invariance, precise |
| Pixel threshold comparison | Compare rendered image against reference with per-channel tolerance | limits, builtin_var |
| Texture sampling reference | Compute reference via `tcu::TextureAccess` sampling | texture_functions, texture_gather |
| CPU-side buffer comparison | Read back output buffer, compare against CPU-computed expected values | atomic_operations, opaque_type_indexing, bfloat16, shader_expect_assume |
| Smoke test (monotonicity) | Verify a value is non-zero and non-decreasing | shader_clock |
| Two-draw rendering | First draw identifies active fragments, second draw verifies helper invocation data | helper_invocations |
| Amber verification | Each `.amber` file defines its own pass/fail criteria | combined_operations, crash_test, logical_copy |
| ShaderLibrary value comparison | Render with shader, compare output against expected values from `.test` value blocks | arrays, conditionals, constant_expressions, constants, conversions, functions, linkage, scoping, swizzles, 440.linkage |

## Links to Level-3 Documentation

- [vktShaderLibrary.cpp.md](../testfiles/glsl/vktShaderLibrary.cpp.md) — ShaderLibrary infrastructure (ES310 + 440 groups)
- [vktShaderRenderDerivateTests.cpp.md](../testfiles/glsl/vktShaderRenderDerivateTests.cpp.md) — derivate
- [vktShaderRenderDiscardTests.cpp.md](../testfiles/glsl/vktShaderRenderDiscardTests.cpp.md) — discard, demote
- [vktShaderRenderIndexingTests.cpp.md](../testfiles/glsl/vktShaderRenderIndexingTests.cpp.md) — indexing
- [vktShaderRenderInvarianceTests.cpp.md](../testfiles/glsl/vktShaderRenderInvarianceTests.cpp.md) — invariance, precise
- [vktShaderRenderLimitTests.cpp.md](../testfiles/glsl/vktShaderRenderLimitTests.cpp.md) — limits
- [vktShaderRenderLoopTests.cpp.md](../testfiles/glsl/vktShaderRenderLoopTests.cpp.md) — loops
- [vktShaderRenderMatrixTests.cpp.md](../testfiles/glsl/vktShaderRenderMatrixTests.cpp.md) — matrix
- [vktShaderRenderOperatorTests.cpp.md](../testfiles/glsl/vktShaderRenderOperatorTests.cpp.md) — operator
- [vktShaderRenderReturnTests.cpp.md](../testfiles/glsl/vktShaderRenderReturnTests.cpp.md) — return
- [vktShaderRenderStructTests.cpp.md](../testfiles/glsl/vktShaderRenderStructTests.cpp.md) — struct
- [vktShaderRenderSwitchTests.cpp.md](../testfiles/glsl/vktShaderRenderSwitchTests.cpp.md) — switch
- [vktShaderRenderTextureFunctionTests.cpp.md](../testfiles/glsl/vktShaderRenderTextureFunctionTests.cpp.md) — texture_functions
- [vktShaderRenderTextureGatherTests.cpp.md](../testfiles/glsl/vktShaderRenderTextureGatherTests.cpp.md) — texture_gather
- [vktShaderRenderBuiltinVarTests.cpp.md](../testfiles/glsl/vktShaderRenderBuiltinVarTests.cpp.md) — builtin_var
- [vktShaderBuiltinTests.cpp.md](../testfiles/glsl/vktShaderBuiltinTests.cpp.md) — builtin
- [vktOpaqueTypeIndexingTests.cpp.md](../testfiles/glsl/vktOpaqueTypeIndexingTests.cpp.md) — opaque_type_indexing
- [vktAtomicOperationTests.cpp.md](../testfiles/glsl/vktAtomicOperationTests.cpp.md) — atomic_operations
- [vktShaderClockTests.cpp.md](../testfiles/glsl/vktShaderClockTests.cpp.md) — shader_clock
- [vktShaderHelperInvocationsTests.cpp.md](../testfiles/glsl/vktShaderHelperInvocationsTests.cpp.md) — helper_invocations
- [vktShaderBFloat16Tests.cpp.md](../testfiles/glsl/vktShaderBFloat16Tests.cpp.md) — bfloat16
- [vktShaderExpectAssumeTests.cpp.md](../testfiles/glsl/vktShaderExpectAssumeTests.cpp.md) — shader_expect_assume
- [vktAmberGlslTests.cpp.md](../testfiles/glsl/vktAmberGlslTests.cpp.md) — combined_operations, crash_test, logical_copy
