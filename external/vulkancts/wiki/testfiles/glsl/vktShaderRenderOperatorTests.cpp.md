# Shader Operator Tests

## Overview

Tests GLSL operators and built-in functions including unary operators (negation, logical not, bitwise not, increment, decrement), binary operators (arithmetic, bitwise, shift, and their compound assignment variants), common built-in functions (min, max, clamp), vector relational/comparison functions (lessThan, greaterThan, equal, notEqual, any, all, not), the ternary selection operator (`?:`), and the sequence operator (`,`). Tests are parameterized across data types (float, int, uint, bool and their vector variants), precision qualifiers, and shader stages.

## Role

Both registration and implementation. The `ShaderOperatorTests` class (line 1967) serves as the `TestCaseGroup` that registers the `glsl.operator` hierarchy, and the same source file contains the `ShaderOperatorCase` class and all evaluation functions.

Source: [vktShaderRenderOperatorTests.cpp](../../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp)

## Registration Hierarchy

```text
glsl.operator
├── unary_operator
├── binary_operator
├── common_functions
├── float_compare
├── int_compare
├── bool_compare
├── selection
└── sequence
```

## Test Families

- **ShaderOperatorCase**: Single test family for all operator and built-in function tests. Each case is constructed with an evaluation function, a GLSL expression string, and a `ShaderDataSpec` describing input types, output type, precision, and value ranges. The `init` method (line 1988) enumerates all function/operator groups and creates individual test cases.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Function/operator type | 50+ variants across groups | Specific operator or built-in function under test |
| Input scalar size | 1-4 | Component count (scalar through vec4/ivec4/uvec4/bvec4) |
| Precision | `lowp`, `mediump`, `highp` | Precision qualifier (controlled by precision mask per operation) |
| DataType | float, int, uint, bool and vector variants | Data type of operands |
| ShaderType | `vertex`, `fragment` | Shader stage under test |
| Value ranges | Per-input min/max | Input value ranges specified per operation (e.g., float: -1.0 to 1.0, int: -5.0 to 5.0) |

**Operator/function groups and their contents**:

- **unary_operator** (line 2012): `-` (negate), `!` (logical not), `~` (bitwise not), `++`/`--` (pre/post increment/decrement, both effect and result variants)
- **binary_operator** (line 2079): `+`, `-`, `*`, `/`, `%` (arithmetic), `&`, `|`, `^` (bitwise), `<<`, `>>` (shift), and compound assignment variants (`+=`, `-=`, `*=`, `/=`, `%=`, `&=`, `|=`, `^=`, `<<=`, `>>=`)
- **common_functions** (line 2516): `min`, `max`, `clamp` (int, uint, and vec-scalar variants)
- **float_compare** (line 2544): `lessThan`, `lessThanEqual`, `greaterThan`, `greaterThanEqual`, `equal`, `notEqual` (float vector inputs)
- **int_compare** (line 2559): `lessThan`, `lessThanEqual`, `greaterThan`, `greaterThanEqual`, `equal`, `notEqual` (int vector inputs)
- **bool_compare** (line 2574): `equal`, `notEqual`, `any`, `all`, `not` (bool vector inputs)
- **selection** (line 2805): `?:` ternary operator across all data types
- **sequence** (line 2861): `,` comma operator with `no_side_effects` and `side_effects` sub-groups

## Support/Feature Requirements

None beyond core Vulkan. All tests use standard GLSL 310 es features.

## Verification Methods

ShaderRenderCase-based reference comparison using `ShaderEvalFunc` callbacks. Each operation has a corresponding C++ evaluation function (e.g., `eval_negate_float`, `eval_add_vec2`, `eval_lessThan_vec3`) that computes the expected result from the shader inputs. The rendered output is compared against the reference with configurable tolerance via `resultScale`, `resultBias`, `referenceScale`, and `referenceBias` parameters in `ShaderDataSpec`.

## Notes

- Binary operators are tested in three modes: normal operation, assignment side-effect (verifying the variable is modified), and assignment result (verifying the return value of the assignment expression).
- Precision masks control which precision levels are tested per operation. Boolean operations use `PRECMASK_NA` and are tested with mediump interpolators only.
- The `sequence` group is split into `no_side_effects` and `side_effects` sub-groups, where side-effect cases use pre/post increment within the comma expression.
- Bitwise operations and shift operations are restricted to `highp` for uint types due to range requirements.
