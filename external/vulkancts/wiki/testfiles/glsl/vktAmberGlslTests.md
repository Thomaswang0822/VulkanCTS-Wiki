# vktAmberGlslTests.cpp

## Overview

Amber-based GLSL test registration and implementation for the Vulkan CTS. This file defines three test groups under the `glsl` category: `combined_operations`, `crash_test`, and `logical_copy`. Each group creates Amber test cases that reference corresponding `.amber` test files for their verification logic.

## Role

Registration + implementation for Amber-based GLSL tests. The file contains three factory functions (`createCombinedOperationsGroup`, `createCrashTestGroup`, `createLogicalCopyGroup`) that each construct a `tcu::TestCaseGroup` populated with Amber test cases via `createAmberTestCase`.

## Source Code

[vktAmberGlslTests.cpp](../../../modules/vulkan/amber/vktAmberGlslTests.cpp#L1-L106)

## Registration Hierarchy

### glsl.combined_operations

```text
glsl.combined_operations
├── notxor
└── negintdivand
```

### glsl.crash_test

```text
glsl.crash_test
├── divbyzero_vert
├── divbyzero_tesc (requires tessellationShader)
├── divbyzero_tese (requires tessellationShader)
├── divbyzero_geom (requires geometryShader)
├── divbyzero_frag
└── divbyzero_comp
```

### glsl.logical_copy

```text
glsl.logical_copy
├── initialized_struct
└── undefined_memory
```

## Test Families

- **combined_operations**: Two Amber test cases verifying bitwise operation combinations in shaders. `notxor` tests bitwise negation of a bitwise XOR operation; `negintdivand` tests bitwise AND of a negative value that was divided.
- **crash_test**: Six Amber test cases verifying that division by zero in each shader stage does not crash the implementation. Each case targets a specific shader stage (vertex, tessellation control, tessellation evaluation, geometry, fragment, compute).
- **logical_copy**: Two Amber test cases verifying `OpLogicalCopy` behavior on structs. `initialized_struct` tests logical copy of an initialized struct; `undefined_memory` tests logical copy of a struct with undefined memory.

## Parameter Dimensions

| Dimension | Values | Applicable Groups |
|-----------|--------|-------------------|
| Shader stage | vert, tesc, tese, geom, frag, comp | crash_test |
| Operation type | notxor, negintdivand | combined_operations |
| Struct state | initialized, undefined | logical_copy |

## Support/Feature Requirements

| Test Case | Requirement | Form |
|-----------|-------------|------|
| divbyzero_tesc | Tessellation shader support | `Features.tessellationShader` |
| divbyzero_tese | Tessellation shader support | `Features.tessellationShader` |
| divbyzero_geom | Geometry shader support | `Features.geometryShader` |

All other test cases have no feature requirements.

## Verification Methods

Amber test framework. Each test case references a corresponding `.amber` file (e.g., `notxor.amber`, `divbyzero_vert.amber`, `initialized_struct.amber`) located in the `combined_operations/`, `crash_test/`, or `logical_copy/` subdirectory respectively. The `.amber` files define their own pipelines, shaders, and pass/fail criteria internally.

## Notes

- The three groups are registered under `glslTests` in [vktTestPackage.cpp](../../../modules/vulkan/vktTestPackage.cpp#L1283-L1285), guarded by `#ifndef CTS_USES_VULKANSC`.
- The `createAmberTestCase` function (from `vktAmberTestCase.hpp`) handles loading the `.amber` file and constructing the Vulkan test case from it, including passing any feature requirements.
- The crash_test group covers all six Vulkan shader stages for division-by-zero robustness testing.
