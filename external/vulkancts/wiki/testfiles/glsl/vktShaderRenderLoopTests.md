# Shader Loop Tests

## Overview

Tests GLSL loop constructs including `for`, `while`, and `do-while` loops with various iteration count sources (constant, uniform, dynamic) and a wide range of loop body patterns. Validates that shader compilers correctly handle loop control flow, including break/continue semantics, nested loops, and edge cases such as zero-iteration loops and infinite loops with conditional exits.

## Role

Both registration and implementation. The `ShaderLoopTests` class (line 1513) serves as the `TestCaseGroup` that registers the `glsl.loops` hierarchy, and the same source file contains all test case creation logic via `createGenericLoopCase` and `createSpecialLoopCase`.

Source: [vktShaderRenderLoopTests.cpp](../../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp)

## Registration Hierarchy

```text
glsl.loops
├── generic
└── special
```

## Test Families

- **GenericLoopCase** (`createGenericLoopCase`, line 342): Basic loop iteration tests that exercise a simple body (`res = res.yzwx + vec4(1.0)`) across all combinations of loop type, count type, precision, and data type. Validates that the loop executes the expected number of iterations by comparing the accumulated result against a reference computed by `getLoopEvalFunc` (line 284).
- **SpecialLoopCase** (`createSpecialLoopCase`): Tests specific loop patterns and edge cases defined by the `LoopCase` enum (line 178), covering control flow variations such as empty bodies, break/continue patterns, nested loops, and switch-fallthrough interactions.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| LoopType | `for`, `while`, `do_while` | Loop construct type (enum at line 150) |
| LoopCountType | `constant`, `uniform`, `dynamic` | How the iteration count is determined (enum at line 167) |
| LoopCase | 30 variants (see below) | Special loop body pattern (enum at line 178) |
| Precision | `mediump`, `highp` | Precision qualifier for loop counter |
| DataType | `int`, `float` | Data type of the loop counter variable |
| ShaderType | `vertex`, `fragment` | Shader stage under test |

**LoopCase variants** (line 178-213): `empty_body`, `infinite_with_unconditional_break_first`, `infinite_with_unconditional_break_last`, `infinite_with_conditional_break`, `single_statement`, `compound_statement`, `sequence_statement`, `no_iterations`, `single_iteration`, `select_iteration_count`, `conditional_continue`, `unconditional_continue`, `only_continue`, `double_continue`, `conditional_break`, `unconditional_break`, `pre_increment`, `post_increment`, `mixed_break_continue`, `vector_counter`, `101_iterations`, `sequence`, `nested`, `nested_sequence`, `nested_tricky_dataflow_1`, `nested_tricky_dataflow_2`, `pre_fallthrough`, `post_fallthrough`, `dowhile_trap`, `ifblock`, `elseblock`.

## Support/Feature Requirements

None beyond core Vulkan. All tests use standard GLSL 310 es features.

## Verification Methods

ShaderRenderCase-based reference comparison. Each test case provides a `ShaderEvalFunc` callback (e.g., `evalLoop0Iters` through `evalLoop3Iters` at lines 267-282) that computes the expected output color from the input coordinates. The rendered output is compared against this reference with appropriate tolerance. The generic loop cases use `getLoopEvalFunc` (line 284) which selects the evaluation function based on the expected number of iterations modulo 4.

## Notes

- The `generic` sub-group organizes tests by loop type and count type (e.g., `for_constant_iterations`), then by precision/data type/shader stage (e.g., `basic_mediump_int_vertex`).
- The `special` sub-group uses the same loop type/count type grouping, then enumerates `LoopCase` variants by shader stage (e.g., `empty_body_vertex`).
- `no_iterations` is skipped for `do_while` loops since do-while always executes at least one iteration (line 1596).
- Uniform setup is handled by `LoopUniformSetup` (line 319) which binds integer and float fraction uniforms needed for non-constant iteration counts.
