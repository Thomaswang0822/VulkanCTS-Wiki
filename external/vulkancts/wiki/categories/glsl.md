## Overview

The `glsl` test category collects Vulkan GLSL tests that check shader-language semantics, generated shader execution, and scripted shader behavior across the ShaderLibrary, ShaderRender, ShaderExecutor, and Amber test paths.

## Background Knowledge

- **GLSL execution models:** the category contains both rendered-image tests, where a shader result is compared with a reference image, and shader-executor tests, where shaders write results that host code reads back and checks. These are the two recurring ways the Level-3 pages make language behavior observable.
- **Generated test matrices:** many families generate leaves from dimensions such as shader stage, data type, precision, resource form, or control-flow variant. A short registration tree therefore represents many concrete mustpass cases.
- **Feature-gated language behavior:** some families require a Vulkan extension or optional device feature. A missing requirement produces a not-supported result rather than a language-semantics failure.

## Category Structure

```text
glsl
├── ShaderLibrary areas: arrays, conditionals, constant_expressions, constants,
│   conversions, functions, linkage, scoping, swizzles, and 440.linkage
├── ShaderRender families: derivate, discard, demote, indexing, invariance,
│   limits, loops, matrix, operator, precise, return, struct, switch,
│   texture_functions, texture_gather, and builtin_var
├── ShaderExecutor families: builtin, opaque_type_indexing, atomic_operations,
│   shader_clock, helper_invocations, bfloat16, and shader_expect_assume
└── Amber families: combined_operations, crash_test, and logical_copy
```

[`createGlslTests()`](../../modules/vulkan/vktTestPackage.cpp#L1215-L1288) assembles these direct children from four source areas rather than from a dedicated `modules/vulkan/glsl/` directory. `invariance` and `precise`, and `discard` and non-VulkanSC `demote`, share their respective Level-3 pages. The non-VulkanSC-only direct children are `demote`, `bfloat16`, the three Amber families, and `shader_expect_assume`.

## How the Families Fit Together

The category tests the same language surface through four complementary test mechanisms.

- **ShaderLibrary** runs declarative `.test` suites for broad GLSL syntax and semantic coverage, including the ES 3.10 groups and `440.linkage`.
- **ShaderRender** turns generated vertex or fragment shader behavior into rendered colors and compares those colors with evaluator-backed reference images; it is suited to expressions, control flow, data layout, and texture operations.
- **ShaderExecutor** runs shader programs that produce host-visible results, enabling resource-indexing, atomic, clock, helper-invocation, and extension-oriented checks.
- **Amber** executes self-contained `.amber` scripts for the small non-VulkanSC set of combined-operation, crash-regression, and logical-copy scenarios.

## Level-3 Pages Navigation

| Registered test family or area | Level-3 page | What to read there |
|---|---|---|
| ShaderLibrary ES 3.10 groups and `440.linkage` | [ShaderLibrary](../testfiles/glsl/ShaderLibrary.md) | Declarative `.test` case generation and ShaderLibrary execution. |
| `builtin_var` | [BuiltinVarTests](../testfiles/glsl/BuiltinVarTests.md) | Built-in shader variables and rendered-image checking. |
| `derivate` | [DerivateTests](../testfiles/glsl/DerivateTests.md) | Derivative behavior and interval-based reference evaluation. |
| `discard`, `demote` | [DiscardTests](../testfiles/glsl/DiscardTests.md) | Fragment discard and the non-VulkanSC demote variants. |
| `indexing` | [IndexingTests](../testfiles/glsl/IndexingTests.md) | Indexing behavior in ShaderRender cases. |
| `invariance`, `precise` | [InvarianceTests](../testfiles/glsl/InvarianceTests.md) | Invariant and precise qualifier behavior. |
| `limits` | [LimitTests](../testfiles/glsl/LimitTests.md) | Language-limit cases and threshold comparisons. |
| `loops` | [LoopTests](../testfiles/glsl/LoopTests.md) | Generated loop-control-flow cases. |
| `matrix` | [MatrixTests](../testfiles/glsl/MatrixTests.md) | Matrix operators, functions, and the matrix evaluator. |
| `operator` | [OperatorTests](../testfiles/glsl/OperatorTests.md) | Generated operators, built-ins, and the operator oracle. |
| `return` | [ReturnTests](../testfiles/glsl/ReturnTests.md) | Returns from helpers, `main()`, and loop bodies. |
| `struct` | [StructTests](../testfiles/glsl/StructTests.md) | Local and `std140` uniform-block structures. |
| `switch` | [SwitchTests](../testfiles/glsl/SwitchTests.md) | Generated switch selectors, labels, fall-through, and nesting. |
| `texture_functions` | [TextureFunctionTests](../testfiles/glsl/TextureFunctionTests.md) | Sampling, fetch, query, sparse, and feature-gated texture paths. |
| `texture_gather` | [TextureGatherTests](../testfiles/glsl/TextureGatherTests.md) | Gather forms, offsets, and texture-gather verification. |
| `builtin` | [BuiltinTests](../testfiles/glsl/BuiltinTests.md) | Common, integer, packing, precision, and conversion built-ins. |
| `opaque_type_indexing` | [OpaqueTypeIndexingTests](../testfiles/glsl/OpaqueTypeIndexingTests.md) | Opaque-resource indexing and storage-buffer support paths. |
| `atomic_operations` | [AtomicOperationTests](../testfiles/glsl/AtomicOperationTests.md) | Atomic operation matrices, memory forms, and result validation. |
| `shader_clock` | [ShaderClockTests](../testfiles/glsl/ShaderClockTests.md) | Shader-clock extension operations and output checks. |
| `helper_invocations` | [ShaderHelperInvocationsTests](../testfiles/glsl/ShaderHelperInvocationsTests.md) | Helper-invocation behavior, passes, and readback. |
| `bfloat16` | [ShaderBFloat16Tests](../testfiles/glsl/ShaderBFloat16Tests.md) | Non-VulkanSC BFloat16 dot, constant, and composite tests. |
| `shader_expect_assume` | [ShaderExpectAssumeTests](../testfiles/glsl/ShaderExpectAssumeTests.md) | Non-VulkanSC `expectKHR` and `assumeKHR` cases. |
| `combined_operations`, `crash_test`, `logical_copy` | [AmberGlslTests](../testfiles/glsl/AmberGlslTests.md) | Non-VulkanSC Amber-scripted GLSL scenarios. |

## Category Notes

The shared category aggregator lives in [`vktTestPackage.cpp`](../../modules/vulkan/vktTestPackage.cpp#L1215-L1288). Detailed parameter matrices, support checks, shader walkthroughs, and result-validation mechanics remain in the corresponding Level-3 pages.
